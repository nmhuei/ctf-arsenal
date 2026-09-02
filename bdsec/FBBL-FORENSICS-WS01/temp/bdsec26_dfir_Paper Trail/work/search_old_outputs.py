#!/usr/bin/env python3
from pathlib import Path
import re
root=Path('work/opencode')
terms=[
 rb'external bank',rb'bank account',rb'account id',rb'Rajesh Patel',rb'branch_id',
 rb'pcap_generator',rb'10\.0\.0\.5',rb'EXT-[A-Z]+-[0-9]+',rb'transfer_receipt',
 rb'beneficiary',rb'wire transfer',rb'SWIFT',rb'IBAN',rb'routing'
]
rx=re.compile(b'|'.join(b'(?:'+t+b')' for t in terms),re.I)
for p in sorted(root.glob('tool_*')):
    data=p.read_bytes()
    print(f'\n### {p} size={len(data)}')
    seen=0
    for m in rx.finditer(data):
        a=max(0,m.start()-180); b=min(len(data),m.end()+400)
        chunk=data[a:b].replace(b'\x00',b' ')
        try:s=chunk.decode('utf-8','replace').replace('\r',' ').replace('\n',' ')
        except:s=repr(chunk)
        print(f'@{m.start()} {s}')
        seen+=1
        if seen>=120:
            print('... capped ...'); break
    print('matches_shown',seen)
