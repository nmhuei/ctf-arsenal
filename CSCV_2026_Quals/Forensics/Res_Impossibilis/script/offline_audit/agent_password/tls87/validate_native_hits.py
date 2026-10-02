#!/usr/bin/env python3
"""Corroborate nonce-inversion candidates using independent TLS75 records."""
from pathlib import Path
import json, sys
from Crypto.Cipher import AES
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
raw=(BASE/'tls75_server.bin').read_bytes()
records=json.loads((BASE/'agent_archive/tls87/tls75_server_records.json').read_text())
def decrypt(key, nonce, i):
    r=records[i]; p=r['payload_offset']; end=r['end']
    g=AES.new(key,AES.MODE_GCM,nonce=nonce); g.update(raw[r['offset']:p])
    return g.decrypt_and_verify(raw[p:end-16],raw[end-16:end])
def nonce(iv, seq):return (iv^seq).to_bytes(12,'big')
results=[]
for line in Path(sys.argv[1]).read_text().splitlines():
    hit=json.loads(line); key=bytes.fromhex(hit['key']); n=bytes.fromhex(hit['j0'])[:12]
    first=decrypt(key,n,6)
    out={**hit,'record6_plaintext':first.hex(),'independent_records':[]}
    # Record6 seq3 is the expected application epoch; bounded alternatives allow extra tickets.
    for s6 in [3]+[x for x in range(16) if x!=3]:
        iv=int.from_bytes(n,'big')^s6
        for s4 in range(16):
            try: p4=decrypt(key,nonce(iv,s4),4)
            except ValueError: continue
            p5=decrypt(key,nonce(iv,s4+1),5)
            name=f'tls75_verified_{key.hex()}'
            (HERE/(name+'_record4.bin')).write_bytes(p4)
            (HERE/(name+'_record5.bin')).write_bytes(p5)
            out['independent_records'].append({'record6_seq':s6,'record4_seq':s4,'record5_seq':s4+1,'base_iv':iv.to_bytes(12,'big').hex(),'record4_length':len(p4),'record5_length':len(p5),'output_prefix':name})
    results.append(out)
path=Path(sys.argv[1]).with_suffix('.validated.json');path.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'candidates':len(results),'corroborated':sum(bool(x['independent_records']) for x in results),'report':str(path)}))
