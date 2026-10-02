"""Locate known ZIPCrypto states in offline memory, including 64-bit layouts."""
from pathlib import Path
import json, mmap, struct, subprocess, sys
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from verify_zip_evidence import TABLE, INITIAL

archive = (BASE / 'archive_from_central.zip').read_bytes()
report = json.loads((BASE / 'archive_central_recovery.json').read_text())
states = {'initial': INITIAL}
for index, entry in enumerate(report['entries']):
    if not entry['complete']:
        continue
    off = entry['local_offset']
    h = struct.unpack_from('<4s5H3I2H', archive, off)
    start = off + 30 + h[9] + h[10]
    a, b, c = INITIAL
    for i, enc in enumerate(archive[start:start + h[7]]):
        t = (c & 65535) | 2
        value = enc ^ ((t * (t ^ 1) >> 8) & 255)
        a = (a >> 8) ^ TABLE[(a ^ value) & 255]
        b = ((b + (a & 255)) * 134775813 + 1) & 0xffffffff
        c = (c >> 8) ^ TABLE[(c ^ (b >> 24)) & 255]
        if i == 11:
            states[f'{index}_after_header'] = (a, b, c)
    states[f'{index}_after_data'] = (a, b, c)

patterns = {}
for name, state in states.items():
    for endian in ('<', '>'):
        for i, value in enumerate(state):
            needle = struct.pack(endian + 'I', value)
            patterns.setdefault(needle, []).append((name, endian, i))
regex = '|'.join(''.join(f'\\x{b:02x}' for b in pat) for pat in patterns)
memfile = BASE.parent / 'evidence/mem.clean'
p = subprocess.run(['rg', '--text', '--json', '--multiline', '--no-unicode', '-e', regex,
                    str(memfile)], capture_output=True)
assert p.returncode in (0, 1), p.stderr
offsets = []
for line in p.stdout.splitlines():
    event = json.loads(line)
    if event['type'] == 'match':
        data = event['data']
        offsets.extend(data['absolute_offset'] + sub['start'] for sub in data['submatches'])
matches, singles = [], []
with memfile.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    for off in offsets:
        needle = m[off:off + 4]
        for name, endian, word in patterns[needle]:
            state = states[name]
            found = []
            for j, value in enumerate(state):
                if j == word:
                    continue
                other = struct.pack(endian + 'I', value)
                lo, hi = max(0, off - 128), off + 132
                pos = m.find(other, lo, hi)
                if pos >= 0:
                    found.append({'word': j, 'relative': pos - off})
            row = {'state': name, 'endian': endian, 'word': word, 'file': hex(off)}
            if found:
                row['nearby_words'] = found
                row['context_hex'] = m[max(0,off - 128):off + 256].hex()
                matches.append(row)
            singles.append(row)
(HERE / 'zip_state_scan.json').write_text(json.dumps({'states': states, 'near_matches': matches,
                                                   'single_word_hits': singles}, indent=2))
print(json.dumps({'states': len(states), 'single_word_hits': len(singles), 'near_matches': matches}, indent=2))
