"""Bounded, read-only search for a conventional collector unwind header.

The verified ELF records GNU_EH_FRAME at VA 0x403190, size 0x7c.
Assuming the conventional 12-byte header and 8-byte entries gives 14 FDEs.
This assumption and four candidate distances do not cover every encoding.
"""
from pathlib import Path
import json
import mmap
import struct

HERE = Path(__file__).resolve().parent
MEM = HERE.parents[1] / "evidence/mem.clean"
rows = []
with MEM.open("rb") as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
    for distance in (0x78, 0x7c, 0x80, 0x84):
        pattern = b"\x01\x1b\x03\x3b" + struct.pack("<II", distance, 14)
        offset = 0
        while True:
            offset = data.find(pattern, offset)
            if offset < 0:
                break
            pairs = [struct.unpack_from("<ii", data, offset + 12 + 8 * i)
                     for i in range(14)]
            starts = [0x403190 + start for start, _ in pairs]
            valid = all(0x401000 <= start < 0x4022f5 for start in starts)
            rows.append({"offset": hex(offset), "delta": distance,
                         "valid_code_range": valid,
                         "starts": [hex(start) for start in starts]})
            if valid:
                (HERE / f"collector_eh_rodata_{offset:x}.bin").write_bytes(
                    data[max(0, offset - 0x190):offset + 0x2cc])
            offset += 1
(HERE / "eh_frame_candidates.json").write_text(json.dumps(rows, indent=2))
print(json.dumps({"total_candidates": len(rows),
                  "valid": [row for row in rows if row["valid_code_range"]]}))
