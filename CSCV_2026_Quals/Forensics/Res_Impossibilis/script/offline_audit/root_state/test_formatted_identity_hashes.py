"""Bounded C-style formatted identity hash hypotheses; exact ZIP-state checks."""
from pathlib import Path
import ctypes, itertools, json, time, zlib
HERE = Path(__file__).resolve().parent
lib = ctypes.CDLL(str(HERE.parent / 'password_verifier.so'))
lib.setup()
lib.check_password.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
host = 'centosstream9.linuxvmimages.local'
mid = '3601188fbcc04a5da1a59be3b5383dfb'
atoms = [host, 'centosstream9', mid, 'centos', '65cc151a88e54d8d98957d1873632f9b']


def hashes(data):
    result = [('crc32', zlib.crc32(data), 32)]
    for bits in (32, 64):
        mask = (1 << bits) - 1
        prime = 16777619 if bits == 32 else 1099511628211
        seeds = [2166136261] if bits == 32 else [14695981039346656037, 1469598103934665603]
        for seed in seeds:
            a = b = seed
            for c in data:
                a = ((a ^ c) * prime) & mask
                b = ((b * prime) ^ c) & mask
            result.extend([(f'fnv1a{bits}:{seed}', a, bits), (f'fnv1{bits}:{seed}', b, bits)])
        djb2, djbx, sdbm = 5381, 5381, 0
        for c in data:
            djb2 = (djb2 * 33 + c) & mask
            djbx = ((djbx * 33) ^ c) & mask
            sdbm = (sdbm * 65599 + c) & mask
        result.extend([(f'djb2_{bits}', djb2, bits), (f'djbx_{bits}', djbx, bits),
                       (f'sdbm_{bits}', sdbm, bits)])
    return result


bases = set(atoms)
for left, right in ((host, mid), ('centosstream9', mid), ('centos', mid)):
    for a, b in ((left, right), (right, left)):
        for sep in ('', ':', '|', '-', '_', '/', '\n', '::'):
            bases.add(a + sep + b)
values = {}
for base in sorted(bases):
    for name, value, bits in hashes(base.encode()):
        for text in (str(value), f'{value:0{bits // 4}x}', f'{value:0{bits // 4}X}'):
            values.setdefault(text, f'{name}({base})')
for left, right in ((host, mid), ('centosstream9', mid), ('centos', mid)):
    a = hashes(left.encode())
    b = hashes(right.encode())
    for (na, va, ba), (nb, vb, bb) in itertools.product(a, b):
        if ba != bb or ba != 32:
            continue
        for upper, sep in itertools.product((False, True), ('', '-', '_', ':')):
            sa, sb = f'{va:08x}', f'{vb:08x}'
            if upper:
                sa, sb = sa.upper(), sb.upper()
            for text in (sa + sep + sb, sb + sep + sa):
                values.setdefault(text, f'{na}({left}) + {nb}({right})')

prefixes = ['', 'audit', 'AUDIT', 'Audit', 'sysaudit', 'sys_audit', 'SysAudit',
            'collector', 'Collector', 'sys_audit_collector', 'mega', 'MEGA', 'Mega',
            'staging', 'Staging', 'zip', 'ZIP', 'backup', 'Backup', 'exfil', 'Exfil',
            'cscv2026', 'CSCV2026', 'ResImpossibilis', 'M3G4', 'm3ga', 'key', 'KEY']
suffixes = ['', '!', '#', '2026', '_2026', '!2026']
separators = ['', '_', '-', ':', '::', '!', '@', '#']
start = time.monotonic()
count, matches = 0, []
for value, origin in values.items():
    for prefix, separator, suffix in itertools.product(prefixes, separators, suffixes):
        if not prefix and separator:
            continue
        candidate = (prefix + separator + value + suffix).encode()
        if not 13 <= len(candidate) <= 128:
            continue
        count += 1
        if lib.check_password(candidate, len(candidate)):
            row = {'password': candidate.decode(), 'origin': origin,
                   'prefix': prefix, 'separator': separator, 'suffix': suffix}
            matches.append(row)
            print('EXACT KEY MATCH', json.dumps(row), flush=True)
report = {'identity_inputs': len(bases), 'hash_representations': len(values),
          'candidates': count, 'matches': matches, 'seconds': time.monotonic() - start,
          'scope': 'Explicit C-style identity hashes, including two FNV64 offset bases; bounded wrappers'}
(HERE / 'formatted_identity_results.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
