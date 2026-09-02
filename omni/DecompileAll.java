//Decompile all functions to a file
//@author Antigravity
//@category Decompiler

import java.io.File;
import java.io.PrintWriter;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;

public class DecompileAll extends GhidraScript {
    @Override
    public void run() throws Exception {
        File outputFile = new File("/home/light/Workspace/CTF/omni/decompiled_ghidra.c");
        PrintWriter writer = new PrintWriter(outputFile);

        DecompInterface decompInterface = new DecompInterface();
        decompInterface.openProgram(currentProgram);

        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext() && !monitor.isCancelled()) {
            Function function = functions.next();
            writer.println("// Function: " + function.getName() + " at " + function.getEntryPoint());
            try {
                DecompileResults results = decompInterface.decompileFunction(function, 30, monitor);
                if (results != null && results.getDecompiledFunction() != null) {
                    writer.println(results.getDecompiledFunction().getC());
                } else {
                    writer.println("// Failed to decompile");
                }
            } catch (Exception e) {
                writer.println("// Exception: " + e.getMessage());
            }
            writer.println();
        }
        writer.close();
        decompInterface.dispose();
    }
}
