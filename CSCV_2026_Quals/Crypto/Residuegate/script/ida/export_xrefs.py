import ida_hexrays
import ida_bytes
import ida_funcs
import ida_kernwin
import ida_name
import idaapi
import idautils
import idc

OUT = "/home/light/Workspace/CTF/CSCV_2026_Quals/Crypto/Residuegate/script/ida/xrefs.txt"
NEEDLES = (
    "feature_",
    "slot.is_none",
    "invalid target slot",
    "encrypted embedding",
    "rejected",
    "target",
    "embedding",
)


def text_at(ea, length):
    raw = ida_bytes.get_bytes(ea, length)
    return raw.decode("utf-8", "replace") if raw else ""


def main():
    lines = []
    if not ida_hexrays.init_hexrays_plugin():
        lines.append("Hex-Rays unavailable")
    for s in idautils.Strings():
        value = str(s)
        if not any(needle in value for needle in NEEDLES):
            continue
        lines.append(f"STRING {s.ea:#x}: {value!r}")
        for xref in idautils.XrefsTo(s.ea):
            func = ida_funcs.get_func(xref.frm)
            if not func:
                lines.append(f"  XREF {xref.frm:#x} (no function)")
                continue
            name = ida_name.get_name(func.start_ea) or f"sub_{func.start_ea:X}"
            lines.append(f"  XREF {xref.frm:#x} in {name} @ {func.start_ea:#x}")
            try:
                cfunc = ida_hexrays.decompile(func.start_ea)
                lines.append(str(cfunc))
            except Exception as exc:
                lines.append(f"  DECOMPILE ERROR: {exc}")
    with open(OUT, "w") as out:
        out.write("\n".join(lines))
    ida_kernwin.qexit(0)


main()
