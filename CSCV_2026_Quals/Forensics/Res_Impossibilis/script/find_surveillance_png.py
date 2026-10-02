#!/usr/bin/env python3
import mmap,struct,zlib,binascii
from pathlib import Path
p=Path('script/evidence/mem.clean')
needle=b'MetroBank SecOps Audit Console | CaptureID: SCR-2026-X89'
sig=b'\x89PNG\r\n\x1a\n'
with p.open('rb') as f:
 m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 pos=0; occ=[]
 while True:
  i=m.find(needle,pos)
  if i<0: break
  occ.append(i);pos=i+1
 print('metadata occurrences',len(occ))
 for i in occ:
  lo=max(0,i-4_000_000)
  s=m.rfind(sig,lo,i)
  if s<0: continue
  # parse PNG chunks from nearest prior signature, checking CRC and end
  q=s+8; chunks=[]; ok=True; end=None
  try:
   while q+12<=len(m) and q-s<8_000_000:
    n=struct.unpack('>I',m[q:q+4])[0]; typ=m[q+4:q+8]
    if n>20_000_000: ok=False;break
    dat=m[q+8:q+8+n]; crc=struct.unpack('>I',m[q+8+n:q+12+n])[0]
    good=(binascii.crc32(typ+dat)&0xffffffff)==crc
    chunks.append((typ.decode('latin1'),n,good,q-s))
    q+=12+n
    if typ==b'IEND': end=q;break
   if end and ok and all(x[2] for x in chunks):
    blob=m[s:end]
    has=needle in blob
    print('VALID',hex(i),'png',hex(s),'size',len(blob),'metadata',has,'chunks',chunks[:20])
    if has:
     out=Path(f'script/chunks/surveillance_{s:x}.png');out.write_bytes(blob);print('SAVED',out)
   else:
    print('NEAR',hex(i),'prior_png',hex(s),'distance',i-s,'parsed',chunks[:8])
  except Exception as e:
   pass
