import idaapi
import idautils
import idc
import ida_hexrays
import ida_funcs
import ida_auto

ida_auto.auto_wait()

# Ensure 0x0 and 0x7d0 are functions
ida_funcs.add_func(0x7d0)

# Traverse code and define functions
for ea in range(0, idc.get_segm_end(0), 16):
    flags = idc.get_full_flags(ea)
    if idc.is_code(flags) and not ida_funcs.get_func(ea):
        ida_funcs.add_func(ea)

ida_auto.auto_wait()

with open("payload_decompiled.c", "w") as f:
    f.write("// Decompiled Payload Code\n\n")
    for ea in sorted(idautils.Functions()):
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

print("Decompilation of payload finished.")
idc.qexit(0)
