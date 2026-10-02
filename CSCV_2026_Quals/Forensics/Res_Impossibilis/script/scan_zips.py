#!/usr/bin/env python3
import mmap,struct,zipfile,io,hashlib
from pathlib import Path
src=Path('script/evidence/mem.clean')
outdir=Path('script/zips'); outdir.mkdir(exist_ok=True)
with src.open('rb') as f:
    m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
    pos=0; seen=0; good=[]
    while True:
        e=m.find(b'PK\x05\x06',pos)
        if e<0: break
        pos=e+4; seen+=1
        if e+22>len(m): continue
        disk,cdisk,n_disk,n_total,cd_size,cd_off,comlen=struct.unpack_from('<HHHHIIH',m,e+4)
        if disk or cdisk or n_total==0 or n_total>10000 or comlen>65535: continue
        start=e-cd_size-cd_off
        end=e+22+comlen
        size=end-start
        if start<0 or size<=0 or size>20_000_000: continue
        if m[start:start+4]!=b'PK\x03\x04': continue
        blob=m[start:end]
        try:
            z=zipfile.ZipFile(io.BytesIO(blob))
            names=z.namelist()
            bad=z.testzip()  # encrypted entries report password-required via RuntimeError
        except RuntimeError:
            try:
                z=zipfile.ZipFile(io.BytesIO(blob)); names=z.namelist(); bad='encrypted'
            except Exception: continue
        except Exception: continue
        rec=(start,end,size,n_total,names[:12],bad,hashlib.sha256(blob).hexdigest())
        good.append(rec)
        if 50000<=size<=80000 or any('documents_staging' in n for n in names):
            out=outdir/f'zip_{start:x}_{size}.zip';out.write_bytes(blob)
            print('CANDIDATE',rec,'saved',out)
    print('EOCD seen',seen,'valid contiguous zips',len(good))
    print('sizes near target')
    for r in good:
        if 40000<=r[2]<=100000: print(r)
