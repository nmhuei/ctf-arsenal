using System;
using Registry;
using RegistryPlugin.RecentDocs;

var hivePath = args.Length > 0 ? args[0] : "../ez_registry_src/Registry.Test/Hives/NTUSER.DAT";
var hive = new RegistryHiveOnDemand(hivePath);
var key = hive.GetKey(@"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\.pdf");
if (key is null)
{
    Console.WriteLine("KEY_NOT_FOUND");
    return;
}
Console.WriteLine($"KEY={key.KeyPath}");
Console.WriteLine("RAW_VALUE_ORDER:");
foreach (var value in key.Values)
{
    Console.WriteLine($"  {value.ValueName}");
}
var plugin = new RecentDocs();
plugin.ProcessValues(key);
Console.WriteLine("PLUGIN_ORDER:");
foreach (RecentDoc rd in plugin.Values)
{
    Console.WriteLine($"MRU={rd.MruPosition} Value={rd.ValueName} Target={rd.TargetName} Lnk={rd.LnkName} Ext={rd.Extension}");
}
Console.WriteLine("ERRORS:");
foreach (var e in plugin.Errors) Console.WriteLine(e);
