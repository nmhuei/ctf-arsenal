using System;
using Prefetch;

var path = args.Length > 0 ? args[0] : "../ez_jumplist_src/JumpList.Test/TestFiles/Bad/CALC.EXE-3FBEF7FD.pf";
try
{
    var pf = PrefetchFile.Open(path);
    Console.WriteLine($"SourceFilename={pf.SourceFilename}");
    Console.WriteLine($"Version={pf.Header.Version}");
    Console.WriteLine($"Signature={pf.Header.Signature}");
    Console.WriteLine($"FileSize={pf.Header.FileSize}");
    Console.WriteLine($"ExecutableFilename={pf.Header.ExecutableFilename}");
    Console.WriteLine($"Hash={pf.Header.Hash}");
    Console.WriteLine($"ParsingError={pf.ParsingError}");
    Console.WriteLine($"RunCount={pf.RunCount}");
    foreach (var f in pf.Filenames) if (f.Contains("CALC", StringComparison.OrdinalIgnoreCase)) Console.WriteLine($"FilenameHit={f}");
}
catch (Exception ex)
{
    Console.WriteLine($"ERROR={ex.GetType().FullName}: {ex.Message}");
    Console.WriteLine(ex.StackTrace);
}
