using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Registry;
using Registry.Abstractions;

if (args.Length != 1) throw new ArgumentException("usage: exact_key_scan <hive-dir>");
var rootDir = args[0];

static IEnumerable<RegistryKey> Walk(RegistryKey root)
{
    var stack = new Stack<RegistryKey>();
    stack.Push(root);
    while (stack.Count > 0)
    {
        var k = stack.Pop();
        yield return k;
        foreach (var s in k.SubKeys) stack.Push(s);
    }
}

static string Norm(string? s) => (s ?? "").Replace('/', '\\').TrimEnd('\\');
static bool IsTyped(string? s) => Norm(s).EndsWith("\\TypedPaths", StringComparison.OrdinalIgnoreCase) || string.Equals(Norm(s), "TypedPaths", StringComparison.OrdinalIgnoreCase);
static bool IsPdfRecent(string? s) => Norm(s).EndsWith("\\RecentDocs\\.pdf", StringComparison.OrdinalIgnoreCase);
static void DumpValue(KeyValue v)
{
    var hex = Convert.ToHexString(v.ValueDataRaw);
    if (hex.Length > 320) hex = hex[..320] + "...";
    Console.WriteLine($"    VALUE name={v.ValueName!} type={v.ValueType} data={v.ValueData!} offset=0x{v.VkRecord.AbsoluteOffset:X} free={v.VkRecord.IsFree} raw={hex}");
}

foreach (var file in Directory.EnumerateFiles(rootDir).OrderBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase))
{
    if (new FileInfo(file).Length < 4096) continue;
    RegistryHive hive;
    try
    {
        hive = new RegistryHive(file) { RecoverDeleted = true, FlushRecordListsAfterParse = false };
        if (!hive.ParseHive()) continue;
    }
    catch { continue; }

    var findings = new List<Action>();
    foreach (var key in Walk(hive.Root))
    {
        if (!IsTyped(key.KeyPath) && !IsPdfRecent(key.KeyPath)) continue;
        var k = key;
        findings.Add(() =>
        {
            Console.WriteLine($"  ACTIVE path={k.KeyPath!} lastWrite={k.LastWriteTime:O} offset=0x{k.NkRecord.AbsoluteOffset:X} free={k.NkRecord.IsFree}");
            foreach (var v in k.Values) DumpValue(v);
        });
    }
    foreach (var key in hive.DeletedRegistryKeys)
    {
        if (!IsTyped(key.KeyPath) && !IsTyped(key.KeyName) && !IsPdfRecent(key.KeyPath) && !IsPdfRecent(key.KeyName)) continue;
        var k = key;
        findings.Add(() =>
        {
            Console.WriteLine($"  DELETED path={k.KeyPath!} name={k.KeyName!} lastWrite={k.LastWriteTime:O} flags={k.KeyFlags} offset=0x{k.NkRecord.AbsoluteOffset:X} free={k.NkRecord.IsFree}");
            foreach (var v in k.Values) DumpValue(v);
        });
    }
    if (findings.Count == 0) continue;
    Console.WriteLine($"\n=== {Path.GetFileName(file)} size={new FileInfo(file).Length} ===");
    foreach (var f in findings) f();
}
