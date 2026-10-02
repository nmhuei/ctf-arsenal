"""Test explicit formatting hypotheses; never treats log size as proof.

A 33-byte hostname + separator + 16 hex bytes gives 50 bytes. A hypothetical
'Password=' prefix and newline would make a 60-byte log. Neither this label
nor this layout has been recovered. Every candidate must pass all 96 bits.
"""
from pathlib import Path
import base64
import ctypes
import hashlib
import itertools
import json
import time
import zlib

HERE = Path(__file__).resolve().parent
lib = ctypes.CDLL(str(HERE.parent / 'password_verifier.so'))
lib.setup()
lib.check_password.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
HOST = 'centosstream9.linuxvmimages.local'
MID = '3601188fbcc04a5da1a59be3b5383dfb'
BOOT = '65cc151a88e54d8d98957d1873632f9b'
identities = [HOST, 'centosstream9', MID, BOOT, 'centos']
separators = ['', ':', '|', '-', '_', '/', '\n', '@', '.']
bases = set(identities)
for left, right in itertools.permutations(identities, 2):
    for separator in separators:
        bases.add(left + separator + right)
for stamp in ['1788885121', '1788885072', '20260908', '2026-09-08']:
    for identity, separator in itertools.product(identities, separators):
        bases.add(identity + separator + stamp)
        bases.add(stamp + separator + identity)
bases |= {s + '\n' for s in tuple(bases)}


def hashes(data):
    yield 'crc32', zlib.crc32(data), 32
    for bits in (32, 64):
        mask = (1 << bits) - 1
        prime = 16777619 if bits == 32 else 1099511628211
        seeds = [2166136261] if bits == 32 else [14695981039346656037, 1469598103934665603]
        for seed in seeds:
            a = b = seed
            for byte in data:
                a = ((a ^ byte) * prime) & mask
                b = ((b * prime) ^ byte) & mask
            yield f'fnv1a{bits}:{seed}', a, bits
            yield f'fnv1{bits}:{seed}', b, bits
        a, b, c = 5381, 5381, 0
        for byte in data:
            a = (a * 33 + byte) & mask
            b = ((b * 33) ^ byte) & mask
            c = (c * 65599 + byte) & mask
        yield f'djb2{bits}', a, bits
        yield f'djbx{bits}', b, bits
        yield f'sdbm{bits}', c, bits


values = {}
for source in sorted(bases):
    for name, value, bits in hashes(source.encode()):
        for formatted in (f'{value:0{bits//4}x}', f'{value:0{bits//4}X}', str(value)):
            values.setdefault(formatted, {'source': source, 'hash': name})
    for name in ('md5', 'sha1', 'sha256', 'sha512'):
        digest = hashlib.new(name, source.encode()).digest()
        forms = [digest.hex(), digest.hex().upper(), base64.b64encode(digest).decode()]
        for whole in forms:
            for formatted in (whole, whole[:16], whole[-16:], whole[:8], whole[-8:]):
                values.setdefault(formatted, {'source': source, 'hash': name})

started = time.monotonic()
counts = {'tested': 0, 'length50': 0}
matches = []
for hashed, provenance in values.items():
    for identity in (HOST, 'centosstream9', 'centos', MID):
        for separator in ('', '_', '-', ':', '.', '@', '#', '|'):
            for candidate in (identity + separator + hashed, hashed + separator + identity):
                raw = candidate.encode()
                counts['tested'] += 1
                counts['length50'] += len(raw) == 50
                if lib.check_password(raw, len(raw)):
                    row = {'candidate': candidate, 'provenance': provenance,
                           'identity': identity, 'separator': separator}
                    matches.append(row)
                    print('EXACT MATCH', json.dumps(row), flush=True)
report = {'hypothesis': 'Observed identity outside a formatted hash; not a recovered formula',
          'hypothetical_log': 'Password=<hostname><separator><16 hex characters>\\n',
          'hostname_length': len(HOST), 'source_bases': len(bases),
          'hash_representations': len(values), 'counts': counts, 'matches': matches,
          'seconds': time.monotonic() - started}
(HERE / 'identity_plus_hash_results.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
