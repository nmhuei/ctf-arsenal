#!/usr/bin/env python3
import mmap,struct,binascii,hashlib
from pathlib import Path
src=Path('script/evidence/mem.clean')
out=Path('script/pngs')
out.mkdir(exist_ok=True)
sig=b'\x89PNG\r\n\x1a\n'
seen={}
total=valid=0
with src.open('rb') as f:
    m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
    pos=0
    while True:
        s=m.find(sig,pos)
        if s<0: break
        pos=s+8
        total+=1
        q=s+8
        dims=None
        ok=True
        end=None
        try:
            for _ in range(2000):
                if q+12>len(m):
                    ok=False
                    break
                n=struct.unpack('>I',m[q:q+4])[0]
                typ=m[q+4:q+8]
                if n>50_000_000 or q+12+n>len(m):
                    ok=False
                    break
                dat=m[q+8:q+8+n]
                crc=struct.unpack('>I',m[q+8+n:q+12+n])[0]
                if (binascii.crc32(typ+dat)&0xffffffff)!=crc:
                    ok=False
                    break
                if typ==b'IHDR' and n==13:
                    dims=struct.unpack('>II',dat[:8])
                q+=12+n
                if typ==b'IEND':
                    end=q
                    break
            if not(ok and end and dims):
                continue
            blob=m[s:end]
            sh=hashlib.sha256(blob).hexdigest()
            if sh in seen:
                continue
            seen[sh]=(s,dims,len(blob))
            valid+=1
            w,h=dims
            if len(blob)>=4096 or (w>=300 and h>=200):
                fn=out/f'{s:x}_{w}x{h}_{len(blob)}.png'
                fn.write_bytes(blob)
                print(hex(s),f'{w}x{h}',len(blob),hashlib.md5(blob).hexdigest(),fn)
        except Exception:
            pass
print('signatures',total,'unique_valid',valid,'saved',len(list(out.glob('*.png'))))
