//Decompile all functions
//@category CTF

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.PrintWriter;
import java.io.FileWriter;

public class Decompile extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        PrintWriter writer = new PrintWriter(new FileWriter("decompiled.c"));
        while (funcs.hasNext()) {
            Function f = funcs.next();
            DecompileResults res = decomp.decompileFunction(f, 30, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                writer.println("// Function: " + f.getName() + " @ " + f.getEntryPoint().toString());
                writer.println(res.getDecompiledFunction().getC());
                writer.println();
            }
        }
        writer.close();
    }
}
