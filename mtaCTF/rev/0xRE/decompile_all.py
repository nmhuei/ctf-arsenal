import idaapi
import idautils
import idc
import ida_hexrays

idaapi.auto_wait()

with open("decompiled.c", "w") as f:
    f.write("// Decompiled by IDA Pro Hex-Rays\n\n")
    for ea in idautils.Functions():
        func_name = idc.get_func_name(ea)
        f.write(f"// Function: {func_name} at 0x{ea:X}\n")
        try:
            cfunc = ida_hexrays.decompile(ea)
            if cfunc:
                f.write(str(cfunc) + "\n\n")
            else:
                f.write(f"// Hex-Rays failed to decompile {func_name}\n\n")
        except Exception as e:
            f.write(f"// Exception decompiling {func_name}: {e}\n\n")

print("Decompilation finished.")
idc.qexit(0)
