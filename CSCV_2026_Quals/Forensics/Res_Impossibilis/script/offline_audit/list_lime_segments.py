import struct
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "script/evidence/mem.clean"
size = p.stat().st_size
off = 0
n = 0
with p.open("rb") as f:
    while off < size:
        f.seek(off)
        h = f.read(32)
        if len(h) != 32:
            break
        magic, version, start, end, reserved = struct.unpack("<IIQQQ", h)
        if magic != 0x4c694d45:
            raise SystemExit(f"bad LiME magic at {off:#x}: {magic:#x}")
        print(n, hex(start), hex(end), hex(off + 32), hex(end - start + 1))
        off += 32 + end - start + 1
        n += 1
