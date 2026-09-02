from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

decomp = DecompInterface()
decomp.openProgram(currentProgram)

monitor = ConsoleTaskMonitor()
funcs = currentProgram.getFunctionManager().getFunctions(True)

with open("decompiled.c", "w") as f:
    for func in funcs:
        results = decomp.decompileFunction(func, 30, monitor)
        if results and results.getDecompiledFunction():
            f.write("// Function: " + func.getName() + " @ " + func.getEntryPoint().toString() + "\n")
            f.write(results.getDecompiledFunction().getC())
            f.write("\n\n")
