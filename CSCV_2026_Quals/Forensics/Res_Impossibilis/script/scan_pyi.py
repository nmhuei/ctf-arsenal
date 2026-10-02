#!/usr/bin/env python3
import mmap,struct
from pathlib import Path
p=Path('script/evidence/mem.clean')
magic=b'MEI\x0c\x0b\x0a\x0b\x0e'
with p.open('rb') as f:
 m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
 pos=0; hits=[]
 while True:
  i=m.find(magic,pos)
  if i<0:break
  pos=i+1
  if i+88>len(m):continue
  try:
   pkglen,tocoff,toclen,pyvers=struct.unpack_from('>IIII',m,i+8)
   pylib=m[i+24:i+88].split(b'\0',1)[0].decode('ascii','replace')
  except Exception:continue
  start=i+88-pkglen
  plausible=0< pkglen < 100_000_000 and 0<=tocoff<pkglen and 0<toclen<pkglen and start>=0
  hits.append((i,pkglen,tocoff,toclen,pyvers,pylib,start,plausible,m[start:start+4]))
for h in hits:
 print(h[:-1], 'start4=',h[-1].hex())
