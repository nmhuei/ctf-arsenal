"""Carve physical pages consistent with a short (<=60 byte) cached file."""
from pathlib import Path
import ctypes, json, mmap, struct
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
lib = ctypes.CDLL(str(BASE / 'password_verifier.so'))
lib.setup()
lib.find_password.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
                             ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
rows, matches = [], []
with (BASE.parent / 'evidence/mem.clean').open('rb') as f, mmap.mmap(
        f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    pos = 0
    while pos < len(m):
        magic, version, start, end, _ = struct.unpack_from('<IIQQQ', m, pos)
        assert magic == 0x4c694d45
        file_start = pos + 32
        for physical in range((start + 4095) & ~4095, end - 4094, 4096):
            off = file_start + physical - start
            b = m[off:off + 128]
            if b[60:] != bytes(68) or not any(b[44:60]):
                continue
            if m[off + 128:off + 4096] != bytes(3968):
                continue
            data = b[:60]
            first, length = ctypes.c_size_t(), ctypes.c_size_t()
            if lib.find_password(data, len(data), ctypes.byref(first), ctypes.byref(length)):
                matches.append({'file': hex(off), 'offset': first.value,
                                'password_hex': data[first.value:first.value + length.value].hex()})
            rows.append({'file': hex(off), 'physical': hex(physical), 'hex': data.hex(),
                         'text': data.rstrip(b'\0').decode(errors='replace')})
        pos = file_start + end - start + 1
(HERE / 'short_page_candidates.json').write_text(json.dumps(rows, indent=2))
(HERE / 'short_page_matches.json').write_text(json.dumps(matches, indent=2))
print(json.dumps({'candidates': len(rows), 'password_matches': matches,
                  'printable_candidates': [r for r in rows if all(
                      32 <= b <= 126 or b in (0, 9, 10, 13) for b in bytes.fromhex(r['hex']))]}, indent=2))
