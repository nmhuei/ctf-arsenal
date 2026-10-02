#!/usr/bin/env python3
"""Bounded offline tests against already recovered ZipCrypto password state.

This tests hypotheses, not evidence that any candidate is the original password.
No evidence files are modified. Run from any directory.
"""
from pathlib import Path
import base64
import ctypes
import hashlib
import itertools
import json
import struct
import time
import zlib

HERE = Path(__file__).resolve().parent
lib = ctypes.CDLL(str(HERE.parent / 'password_verifier.so'))
lib.setup()
lib.find_password.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
libc = ctypes.CDLL('libc.so.6')
libc.srand.argtypes = [ctypes.c_uint]
libc.rand.restype = ctypes.c_int
counts = {}
hits = []
started = time.monotonic()

def scan(value, family, note):
    counts[family] = counts.get(family, 0) + 1
    start, length = ctypes.c_size_t(), ctypes.c_size_t()
    if lib.find_password(value, len(value), ctypes.byref(start), ctypes.byref(length)):
        password = value[start.value:start.value + length.value]
        hit = dict(family=family, note=note, offset=start.value,
                   password_hex=password.hex(), length=len(password),
                   contains_nul=(b'\0' in password))
        hits.append(hit)
        print('MATCH', json.dumps(hit), flush=True)

def representations(value):
    yield 'raw', value
    yield 'base64', base64.b64encode(value)
    yield 'base64url', base64.urlsafe_b64encode(value)
    yield 'base32', base64.b32encode(value)
    yield 'base32lower', base64.b32encode(value).lower()
    yield 'base85', base64.b85encode(value)
    yield 'ascii85', base64.a85encode(value)
    yield 'hex', value.hex().encode()
    yield 'HEX', value.hex().upper().encode()

mid = '3601188fbcc04a5da1a59be3b5383dfb'
boot = '65cc151a88e54d8d98957d1873632f9b'
fqdn = 'centosstream9.linuxvmimages.local'
short = 'centosstream9'
seeds = set(range(1788884900, 1788885301)) | {0, 1}
for s in (mid, boot):
    for i in range(0, 32, 8):
        seeds.add(int(s[i:i+8], 16))
for s in (mid, boot, short, fqdn, 'centos'):
    seeds.add(zlib.crc32(s.encode()))

# Includes the standard unseeded glibc state (srand(1)), raw shifted bytes,
# packed words and encodings missing from test_password_rng.py.
# Every substring of each sequence up to128bytes is checked, including all
# C-string prefixes ending before a NUL. A matching sequence containing NUL
# would need an explicit-length password API and is marked separately.
for seed in sorted(seeds):
    libc.srand(seed)
    values = [libc.rand() for _ in range(96)]
    streams = [(f'byte{shift}', bytes((v >> shift) & 255 for v in values))
               for shift in (0, 8, 16, 24)]
    streams += [('u32le', b''.join(struct.pack('<I', v) for v in values)),
                ('u32be', b''.join(struct.pack('>I', v) for v in values)),
                ('u16le', b''.join(struct.pack('<H', v & 65535) for v in values)),
                ('u16be', b''.join(struct.pack('>H', v & 65535) for v in values))]
    for stream_name, stream in streams:
        for enc, value in representations(stream):
            scan(value, 'rng_raw_and_encodings', f'{seed}:{stream_name}:{enc}')
print('RNG completed', counts, flush=True)

# Identity-derived inputs with exact scope preserved in this source.
# All source atoms were observed in challenge memory or metadata.
identifiers = [mid, boot, mid.upper(), boot.upper()]
for s in (mid, boot):
    identifiers.append(f'{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}')
hosts = [short, fqdn]
times = ['1788885121', '20260908', '2026-09-08', '20260908163201', '20260908233201']
separators = ['', '_', '-', ':', '|', '@', '.', '/', '\n', '\r\n']
bases = set(identifiers + hosts + times + ['centos', 'sys_audit_collector', 'documents_staging'])
for left, right in ((identifiers, hosts), (identifiers, times),
                    (hosts, times), (identifiers, ['centos'])):
    for a, b, sep in itertools.product(left, right, separators):
        bases.add(a + sep + b)
        bases.add(b + sep + a)
for a in tuple(bases):
    bases.add(a + '\n')

for s in sorted(bases):
    source = s.encode()
    for encoding, value in representations(source):
        scan(value, 'identity_encodings', f'{s!r}:{encoding}')
    for name in ('md5', 'sha1', 'sha256', 'sha512'):
        digest = hashlib.new(name, source).digest()
        for encoding, value in representations(digest):
            scan(value, 'identity_digest_encodings', f'{s!r}:{name}:{encoding}')
    # Compact inlined hashes need no imported crypto library. Values longer
    # than12printable bytes are not excluded by the existing bkcrack result.
    mask = (1 << 64) - 1
    fnv1a = fnv1 = 14695981039346656037
    djb2, sdbm = 5381, 0
    for b in source:
        fnv1a = ((fnv1a ^ b) * 1099511628211) & mask
        fnv1 = ((fnv1 * 1099511628211) ^ b) & mask
        djb2 = (djb2 * 33 + b) & mask
        sdbm = (sdbm * 65599 + b) & mask
    for name, number in [('fnv1a64', fnv1a), ('fnv164', fnv1),
                         ('djb264', djb2), ('sdbm64', sdbm)]:
        for value in (f'{number:016x}', f'{number:016X}', str(number)):
            scan(value.encode(), 'identity_inlined_hashes', f'{s!r}:{name}')
print('Identity hashes completed', counts, flush=True)

# C snprintf precision/truncation possibilities: prior structured test used
# full identifiers and selected manually chosen half-id variants. Test each
# observed id prefix/suffix length, paired with the actual hostname/user.
for ident in (mid, boot):
    for n in range(1, 33):
        for fragment in {ident[:n], ident[-n:]}:
            for host, sep in itertools.product(hosts + ['centos'], separators):
                for s in (host + sep + fragment, fragment + sep + host):
                    scan(s.encode(), 'truncated_identity', s)
                    scan((s + '\n').encode(), 'truncated_identity', s + '\n')

report = dict(counts=counts, hits=hits, source_bases=len(bases),
              rng_seeds=len(seeds), rng_outputs_per_seed=96,
              maximum_candidate_length=128,
              verification='Exact three-word ZipCrypto initial state',
              elapsed_seconds=round(time.monotonic()-started, 3))
(HERE / 'bounded_hypotheses_results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
