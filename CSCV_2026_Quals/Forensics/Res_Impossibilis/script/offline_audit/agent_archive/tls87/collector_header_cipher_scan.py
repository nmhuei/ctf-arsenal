from pathlib import Path
import json,struct,hashlib,subprocess,mmap
from Crypto.Cipher import AES
P=Path(__file__).resolve().parent;H=P.parents[1];MEM=H.parent/'evidence/mem.clean';plain=(H/'collector_pagecache_exact.bin').read_bytes()[:4096];assert hashlib.sha256(plain).hexdigest()=='f34667b6cb71989f1084c85a0e1bcd10358dfa797753ffefdac14fa0e059889f'
w=[x&0xffffffff for x in [-1230090044,2127323314,-1059689052,1415825335,-2074817314,253067825,763488977,855944017]];key=struct.pack('>4I',*(w[i]^w[i+4] for i in range(4)));iv=int.from_bytes(struct.pack('>4I',w[4],w[5],0,0),'big');cipher=AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=iv).encrypt(plain);sigs={}
for offset in range(0,4096-32,32):
 original=cipher[offset:offset+32]
 for width in (1,2,4,8):
  sig=b''.join(original[i:i+width][::-1] for i in range(0,32,width))
  if b'\n' not in sig:sigs[sig]=(offset,width)
pattern='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigs);r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*32,'--regexp',pattern,str(MEM)],capture_output=True);assert r.returncode in(0,1),r.stderr;hits=[]
with MEM.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for line in r.stdout.splitlines():
  pos=int(line.split(b':')[0]);off,width=sigs[m[pos:pos+32]];hits.append({'memory':hex(pos),'collector_offset':off,'word_byte_reversal':width})
report={'file_key_words':w,'header_plain_sha256':hashlib.sha256(plain).hexdigest(),'signatures':len(sigs),'hits':hits};(P/'collector_header_cipher_results.json').write_text(json.dumps(report,indent=2));print('SIGNATURES',len(sigs),'HITS',hits)
