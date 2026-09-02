using System;
using System.IO;
using Registry;
using Registry.Abstractions;
using RegistryPlugin.RecentDocs;

var dir = args.Length > 0 ? args[0] : "../ez_registry_src/Registry.Test/Hives";

IEnumerable<RegistryKey> Walk(RegistryKey key)
{
    yield return key;
    foreach (var child in key.SubKeys)
        foreach (var nested in Walk(child))
            yield return nested;
}

foreach (var file in Directory.EnumerateFiles(dir))
{
    try
    {
        if (new FileInfo(file).Length < 4096) continue;
        var hive = new RegistryHive(file) { FlushRecordListsAfterParse = true, RecoverDeleted = false };
        if (!hive.ParseHive()) continue;
        foreach (var key in Walk(hive.Root))
        {
            var normalized = key.KeyPath.Replace('/', '\\');
            if (!normalized.EndsWith(@"\RecentDocs\.pdf", StringComparison.OrdinalIgnoreCase)) continue;
            Console.WriteLine($"FILE={Path.GetFileName(file)} KEY={key.KeyPath}");
            var plugin = new RecentDocs();
            plugin.ProcessValues(key);
            foreach (RecentDoc rd in plugin.Values)
                Console.WriteLine($"  MRU={rd.MruPosition} Value={rd.ValueName} Target={rd.TargetName} Lnk={rd.LnkName}");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"ERROR FILE={Path.GetFileName(file)} TYPE={ex.GetType().Name} MSG={ex.Message}");
    }
}
