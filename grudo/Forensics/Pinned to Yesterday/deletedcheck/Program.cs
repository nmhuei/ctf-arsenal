using System;
using System.Linq;
using System.Text;
using Registry;
using Registry.Abstractions;

var hivePath = args.Length > 0 ? args[0] : "../ez_registry_src/Registry.Test/Hives/NTUSER.DAT";
var hive = new RegistryHive(hivePath)
{
    RecoverDeleted = true,
    FlushRecordListsAfterParse = false
};
Console.WriteLine($"FILE={hivePath}");
Console.WriteLine($"PARSED={hive.ParseHive()}");
Console.WriteLine($"DELETED_KEYS={hive.DeletedRegistryKeys.Count} UNASSOCIATED_VALUES={hive.UnassociatedRegistryValues.Count}");

static string Utf16Preview(byte[] raw)
{
    try { return Encoding.Unicode.GetString(raw).Replace("\0", "|"); }
    catch { return ""; }
}
static bool Pdfish(string? s) => s?.Contains(".pdf", StringComparison.OrdinalIgnoreCase) == true;
static bool RecentPdfKey(string? s) => s?.Replace('/', '\\').Contains(@"RecentDocs\.pdf", StringComparison.OrdinalIgnoreCase) == true;

Console.WriteLine("DELETED_RECENTDOCS_PDF_KEYS:");
foreach (var key in hive.DeletedRegistryKeys)
{
    if (!RecentPdfKey(key.KeyPath) && !RecentPdfKey(key.KeyName)) continue;
    Console.WriteLine($"KEY Path={key.KeyPath} Name={key.KeyName} LastWrite={key.LastWriteTime:O} Flags={key.KeyFlags} Offset=0x{key.NkRecord.AbsoluteOffset:X} Free={key.NkRecord.IsFree}");
    foreach (var v in key.Values)
        Console.WriteLine($"  VALUE Name={v.ValueName} Data={v.ValueData} RawUTF16={Utf16Preview(v.ValueDataRaw)} Type={v.ValueType} Offset=0x{v.VkRecord.AbsoluteOffset:X} Free={v.VkRecord.IsFree}");
}

Console.WriteLine("UNASSOCIATED_PDF_VALUES:");
foreach (var v in hive.UnassociatedRegistryValues)
{
    var preview = Utf16Preview(v.ValueDataRaw);
    if (!Pdfish(v.ValueData) && !Pdfish(preview)) continue;
    Console.WriteLine($"VALUE Name={v.ValueName} Data={v.ValueData} RawUTF16={preview} Type={v.ValueType} Offset=0x{v.VkRecord.AbsoluteOffset:X} Free={v.VkRecord.IsFree}");
}
