"""Use surviving original-file tail to locate earlier encrypted archive pages."""
from pathlib import Path
import json, mmap, re, struct, subprocess, sys
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from verify_zip_evidence import TABLE
from recover_archive_central import crypt

INV_TABLE = {v >> 24: i for i, v in enumerate(TABLE)}
MULTIPLIER_INVERSE = pow(134775813, -1, 2**32)


def inverse_crc(y, value):
    index = INV_TABLE[y >> 24]
    return (((y ^ TABLE[index]) << 8) | (index ^ value)) & 0xffffffff


def step(state, value):
    a, b, c = state
    a = (a >> 8) ^ TABLE[(a ^ value) & 255]
    b = ((b + (a & 255)) * 134775813 + 1) & 0xffffffff
    c = (c >> 8) ^ TABLE[(c ^ (b >> 24)) & 255]
    return a, b, c


def unstep(state, value):
    a, b, c = state
    old_c = inverse_crc(c, b >> 24)
    old_b = ((b - 1) * MULTIPLIER_INVERSE - (a & 255)) & 0xffffffff
    old_a = inverse_crc(a, value)
    result = old_a, old_b, old_c
    assert step(result, value) == state
    return result


def encrypt_byte(state, value):
    t = (state[2] & 65535) | 2
    return value ^ ((t * (t ^ 1) >> 8) & 255)


def main():
    setup = json.loads((HERE / 'alt_tail_setup.json').read_text())
    keys = tuple(int(x, 16) for x in (HERE / 'alt_tail_bkcrack.log').read_text().splitlines()[-1].split())
    plain = (HERE / 'alt_tail.plain').read_bytes()
    cipher = (HERE / 'alt_tail.cipher').read_bytes()
    state = keys
    for p, c in zip(plain, cipher):
        assert encrypt_byte(state, p) == c
        state = step(state, p)
    tail = (BASE / 'agent_collector/AlternateServices.txt.tail.bin').read_bytes()
    earlier = tail[:setup['plain_offset'] - 4096]
    state = keys
    derived = bytearray(len(earlier))
    for i in range(len(earlier) - 1, -1, -1):
        state = unstep(state, earlier[i])
        derived[i] = encrypt_byte(state, earlier[i])
    logical_start = setup['logical'] - len(derived)
    (HERE / 'alt_tail_derived.cipher').write_bytes(derived)
    patterns = {}
    for off in range(0, len(derived) - 15, 16):
        for layer in ('zip', 'mega'):
            logical = logical_start + off
            b = bytes(derived[off:off + 16])
            if layer == 'mega':
                b = crypt(b, logical)
            patterns.setdefault(b, []).append((layer, logical))
    regex = '|'.join(''.join(f'\\x{b:02x}' for b in needle) for needle in patterns)
    memfile = BASE.parent / 'evidence/mem.clean'
    scan = subprocess.run(['rg', '--text', '--json', '--multiline', '--no-unicode',
                           '-e', regex, str(memfile)], capture_output=True)
    assert scan.returncode in (0, 1), scan.stderr
    hits = []
    for line in scan.stdout.splitlines():
        event = json.loads(line)
        if event['type'] == 'match':
            data = event['data']
            hits.extend(data['absolute_offset'] + sub['start'] for sub in data['submatches'])
    records = []
    with memfile.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        segments, pos = [], 0
        while pos < len(m):
            _, _, start, end, _ = struct.unpack_from('<IIQQQ', m, pos)
            segments.append((start, end + 1, pos + 32))
            pos += 32 + end - start + 1
        for hit in hits:
            for layer, logical in patterns[m[hit:hit + 16]]:
                s, e, fo = next(seg for seg in segments if seg[2] <= hit < seg[2] + seg[1] - seg[0])
                within = (s + hit - fo) % 4096
                base, archive_base = hit - within, logical - within
                lo, hi = max(0, archive_base), min(65408, archive_base + 4096)
                data = m[base + lo - archive_base:base + hi - archive_base]
                if layer == 'mega':
                    data = crypt(data, lo)
                name = f'alt_candidate_{layer}_{base:x}_{lo:x}.bin'
                (HERE / name).write_bytes(data)
                row = {'layer': layer, 'memory': hex(base), 'logical': lo, 'file': name}
                if row not in records:
                    records.append(row)
    report = {'window_keys': [f'{k:08x}' for k in keys], 'verified_cipher_bytes': len(cipher),
              'derived_start': logical_start, 'derived_bytes': len(derived),
              'patterns': len(patterns), 'candidate_pages': records}
    for row in records:
        page = (HERE / row['file']).read_bytes()
        if row['logical'] + len(page) != setup['logical']:
            continue
        overlap_start = logical_start - row['logical']
        if page[overlap_start:] != derived:
            continue
        state = keys
        output = bytearray(len(page))
        for i in range(len(page) - 1, -1, -1):
            old_c = inverse_crc(state[2], state[1] >> 24)
            value = encrypt_byte((0, 0, old_c), page[i])
            state = unstep(state, value)
            assert encrypt_byte(state, value) == page[i]
            output[i] = value
        recovered = bytes(output) + plain
        assert recovered[-len(tail):] == tail
        plain_offset = row['logical'] - setup['plain_start']
        partial_report = {'plain_offset': plain_offset, 'size': len(recovered),
                          'original_tail_overlap_verified': len(tail),
                          'keys_at_681': [f'{k:08x}' for k in state],
                          'full_crc_verified': False}
        (HERE / '37_AlternateServices.partial.txt').write_bytes(recovered)
        (HERE / 'alt_partial_report.json').write_text(json.dumps(partial_report, indent=2))
        report['verified_partial'] = partial_report
    (HERE / 'alt_tail_recovery.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
