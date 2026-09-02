import idautils
import idc
import idaapi
import ida_hexrays
import ida_auto
import ida_pro
import sys

def main():
    print("[*] Waiting for auto-analysis to complete...")
    ida_auto.auto_wait()
    print("[+] Auto-analysis complete.")

    output_path = "/home/light/Workspace/CTF/omni/decompiled.c"
    print(f"[*] Decompiling all functions to {output_path}...")

    if not ida_hexrays.init_hexrays_plugin():
        print("[-] Hex-Rays decompiler is not available!")
        ida_pro.qexit(1)
        return

    with open(output_path, "w") as f:
        for func_ea in idautils.Functions():
            func_name = idc.get_func_name(func_ea)
            f.write(f"// Function: {func_name} (0x{func_ea:X})\n")
            try:
                cfunc = ida_hexrays.decompile(func_ea)
                if cfunc:
                    f.write(str(cfunc))
                    f.write("\n\n")
                else:
                    f.write(f"// Failed to decompile (returned None)\n\n")
            except Exception as e:
                f.write(f"// Exception during decompilation: {e}\n\n")

    print("[+] Decompilation finished.")
    ida_pro.qexit(0)

if __name__ == "__main__":
    main()
