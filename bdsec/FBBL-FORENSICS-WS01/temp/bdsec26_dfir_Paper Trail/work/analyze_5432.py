#!/usr/bin/env python3
import csv, hashlib, math, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

PCAP = Path('work/network_capture.pcap')
OUT = Path('work/pg_streams.csv')
cmd = [
    'tshark','-r',str(PCAP),'-Y','tcp.port==5432 && tcp.len>0',
    '-T','fields','-E','separator=\t','-E','occurrence=f',
    '-e','frame.number','-e','frame.time_epoch','-e','tcp.stream',
    '-e','ip.src','-e','ip.dst','-e','tcp.len','-e','tcp.payload'
]
p = subprocess.run(cmd, capture_output=True, text=True, check=True)
rows = []
streams = defaultdict(dict)
for line in p.stdout.splitlines():
    cols = line.split('\t')
    if len(cols) < 7:
        continue
    frame, ts, stream, src, dst, length, payload_hex = cols[:7]
    if not payload_hex:
        continue
    data = bytes.fromhex(payload_hex.replace(':',''))
    rec = {'frame':int(frame), 'ts':float(ts), 'stream':int(stream), 'src':src, 'dst':dst, 'len':int(length), 'data':data}
    if src == '10.0.0.1':
        m = re.search(rb'branch_id=(\d+)', data)
        if m:
            streams[int(stream)]['branch'] = int(m.group(1))
            streams[int(stream)]['request_frame'] = int(frame)
            streams[int(stream)]['request_ts'] = float(ts)
            streams[int(stream)]['request'] = data.decode(errors='replace')
    elif src == '10.0.0.5':
        streams[int(stream)]['response'] = data
        streams[int(stream)]['response_frame'] = int(frame)
        streams[int(stream)]['response_ts'] = float(ts)

def entropy(b):
    if not b: return 0.0
    c = Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

for stream, d in sorted(streams.items(), key=lambda kv: kv[1].get('request_frame',10**12)):
    if 'branch' not in d or 'response' not in d:
        continue
    b=d['response']
    rows.append({
        'stream':stream,'request_frame':d['request_frame'],'request_ts':d['request_ts'],
        'branch':d['branch'],'response_frame':d.get('response_frame',''),'response_len':len(b),
        'entropy':round(entropy(b),6),'sha256':hashlib.sha256(b).hexdigest(),
        'first16':b[:16].hex(),'last16':b[-16:].hex(),
        'sum_mod256':sum(b)%256,'xor_all':__import__('functools').reduce(lambda x,y:x^y,b,0),
    })
with OUT.open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

print('streams',len(rows))
branches=[r['branch'] for r in rows]
print('branch_range',min(branches),max(branches))
print('branch_freq',dict(sorted(Counter(branches).items())))
print('response_len min/max/mean',min(r['response_len'] for r in rows),max(r['response_len'] for r in rows),round(sum(r['response_len'] for r in rows)/len(rows),2))
print('entropy min/max',min(r['entropy'] for r in rows),max(r['entropy'] for r in rows))
print('first 120 branch sequence:')
print(' '.join(map(str,branches[:120])))
print('A1Z26 <=26:')
print(''.join(chr(64+x) if 1<=x<=26 else '?' for x in branches[:300]))
print('zero-based 0-25:')
print(''.join(chr(65+x) if 0<=x<=25 else '?' for x in branches[:300]))
# Outliers by entropy and length
print('lowest entropy:')
for r in sorted(rows,key=lambda x:x['entropy'])[:20]: print(r)
print('shortest responses:')
for r in sorted(rows,key=lambda x:x['response_len'])[:20]: print(r)
# repeated same response hash
hc=Counter(r['sha256'] for r in rows)
print('duplicate_response_hashes',sum(1 for v in hc.values() if v>1))
# Analyze selected byte/stat projections as text
for key in ['response_len','sum_mod256','xor_all']:
    vals=[r[key] for r in rows]
    print(key,'mod26:', ''.join(chr(65+(v%26)) for v in vals[:300]))
    print(key,'printable:', ''.join(chr(v%128) if 32<=v%128<127 else '.' for v in vals[:300]))
