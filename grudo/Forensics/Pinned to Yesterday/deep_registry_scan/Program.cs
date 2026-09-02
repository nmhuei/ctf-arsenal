using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Registry;
using Registry.Abstractions;

if (args.Length == 0)
{
    Console.Error.WriteLine("Usage: deep_registry_scan <hive-dir>");
    return;
}

var rootDir = args[0];

static IEnumerable<RegistryKey> Walk(RegistryKey root)
{
    var stack = new Stack<RegistryKey>();
    stack.Push(root);
    while (stack.Count > 0)
    {
        var key = stack.Pop();
        yield return key;
        foreach (var sub in key.SubKeys)
            stack.Push(sub);
    }
}

static bool InterestingPath(string? s)
{
    if (string.IsNullOrWhiteSpace(s)) return false;
    s = s.Replace('/', '\\');
    return s.Contains(@"RecentDocs\.pdf", StringComparison.OrdinalIgnoreCase)
        || s.Contains("TypedPaths", StringComparison.OrdinalIgnoreCase);
}

static bool InterestingData(string? s)
{
    if (string.IsNullOrWhiteSpace(s)) return false;
    return s.Contains("ShellBagsExplorer", StringComparison.OrdinalIgnoreCase)
        || s.Contains("ProjectWorkingFolder", StringComparison.OrdinalIgnoreCase)
        || s.Contains(".pdf", StringComparison.OrdinalIgnoreCase);
}

static string RawPreview(byte[] raw)
{
    if (raw.Length == 0) return "";
    var parts = new List<string>();
    try
    {
        var u = Encoding.Unicode.GetString(raw).Replace("\0", "|");
        if (u.Any(c => c >= 32 && c < 127)) parts.Add("UTF16=" + u);
    }
    catch { }
    try
    {
        var a = Encoding.ASCII.GetString(raw).Replace("\0", "|");
        if (a.Any(c => c >= 32 && c < 127)) parts.Add("ASCII=" + a);
    }
    catch { }
    return string.Join(" ; ", parts);
}

foreach (var file in Directory.EnumerateFiles(rootDir).OrderBy(x => x, StringComparer.OrdinalIgnoreCase))
{
    FileInfo fi;
    try { fi = new FileInfo(file); }
    catch { continue; }
    if (fi.Length < 4096) continue;

    RegistryHive hive;
    try
    {
        hive = new RegistryHive(file)
        {
            RecoverDeleted = true,
            FlushRecordListsAfterParse = false,
        };
        if (!hive.ParseHive()) continue;
    }
    catch { continue; }

    var printedHeader = false;
    void Header()
    {
        if (printedHeader) return;
        Console.WriteLine($"\n=== HIVE {Path.GetFileName(file)} size={fi.Length} ===");
        printedHeader = true;
    }

    foreach (var key in Walk(hive.Root))
    {
        var matchingValues = key.Values.Where(v => InterestingData(v.ValueName) || InterestingData(v.ValueData) || InterestingData(RawPreview(v.ValueDataRaw))).ToList();
        if (!InterestingPath(key.KeyPath) && matchingValues.Count == 0) continue;
        Header();
        Console.WriteLine($"ACTIVE KEY path={key.KeyPath} lastWrite={key.LastWriteTime:O} offset=0x{key.NkRecord.AbsoluteOffset:X} free={key.NkRecord.IsFree}");
        foreach (var v in key.Values)
            Console.WriteLine($"  VALUE name={v.ValueName} type={v.ValueType} data={v.ValueData} raw={RawPreview(v.ValueDataRaw)} offset=0x{v.VkRecord.AbsoluteOffset:X} free={v.VkRecord.IsFree}");
    }

    foreach (var key in hive.DeletedRegistryKeys)
    {
        var matchingValues = key.Values.Where(v => InterestingData(v.ValueName) || InterestingData(v.ValueData) || InterestingData(RawPreview(v.ValueDataRaw))).ToList();
        if (!InterestingPath(key.KeyPath) && !InterestingPath(key.KeyName) && matchingValues.Count == 0) continue;
        Header();
        Console.WriteLine($"DELETED KEY path={key.KeyPath} name={key.KeyName} lastWrite={key.LastWriteTime:O} flags={key.KeyFlags} offset=0x{key.NkRecord.AbsoluteOffset:X} free={key.NkRecord.IsFree}");
        foreach (var v in key.Values)
            Console.WriteLine($"  VALUE name={v.ValueName} type={v.ValueType} data={v.ValueData} raw={RawPreview(v.ValueDataRaw)} offset=0x{v.VkRecord.AbsoluteOffset:X} free={v.VkRecord.IsFree}");
    }

    foreach (var v in hive.UnassociatedRegistryValues)
    {
        var preview = RawPreview(v.ValueDataRaw);
        if (!InterestingData(v.ValueName) && !InterestingData(v.ValueData) && !InterestingData(preview)) continue;
        Header();
        Console.WriteLine($"UNASSOCIATED VALUE name={v.ValueName} type={v.ValueType} data={v.ValueData} raw={preview} offset=0x{v.VkRecord.AbsoluteOffset:X} free={v.VkRecord.IsFree}");
    }
}
