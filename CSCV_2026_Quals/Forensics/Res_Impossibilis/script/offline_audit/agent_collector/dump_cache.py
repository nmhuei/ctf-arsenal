"""Index struct-page metadata for mem.dmp and retrieve possible cached source pages.
Acquisition is non-atomic: always validate returned payload independently.
"""
import kernel_walk as k
import struct
import numpy as np
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');MAP=0xffff978f4c1d6ef8;ROOT=0x1294000

def make_index():
 rows=[];mapped=0
 for offset in range(0,0x240000000//4096*64,0x200000):
  pa=k.walk(ROOT,k.VM+offset)
  if pa is None:continue
  fo=k.p2f(pa)
  if fo is None:continue
  length=min(0x200000,0x240000000//4096*64-offset)
  a=np.frombuffer(k.m,dtype='<u8',count=length//8,offset=fo).reshape(-1,8)
  hits=np.flatnonzero(a[:,3]==MAP)
  if len(hits): rows.append(np.column_stack((a[hits,4],(offset//64+hits)*4096)))
  mapped+=length
 index=np.concatenate(rows).astype(np.uint64); index=index[np.argsort(index[:,0])]
 np.save(OUT/'dump_cache_index.npy',index)
 print('mapped_metadata_bytes',mapped,'cache_page_count',len(index),'indexrange',index[0,0],index[-1,0])
 return index

def lookup(fileoffset,index=None):
 if index is None:index=np.load(OUT/'dump_cache_index.npy')
 hits=index[index[:,0]==fileoffset//4096,1]
 return [(int(pa),k.p2f(int(pa))+(fileoffset%4096)) for pa in hits if k.p2f(int(pa)) is not None]

if __name__=='__main__':
 index=make_index()
 import json,hashlib
 targets=[0x3401e040,0x31768040,0x350d3040,0x350d4040,0x350d5040,0x350d7040]
 targets += [k.p2f(p) for p in [0x20dcd1000,0x20dcce000,0x20dcc9000]]
 rows=[]
 for target in targets:
  for pa,fo in lookup(target,index):
   b=k.m[fo:fo+4096];row={'target_file':hex(target),'cache_phys':hex(pa),'cache_file':hex(fo),'nonzero':sum(c!=0 for c in b),'head':b[:64].hex(),'sha256':hashlib.sha256(b).hexdigest()};rows.append(row);print(row)
   (OUT/f'dump_cache_{target:x}_{fo:x}.bin').write_bytes(b)
 (OUT/'dump_cache_targets.json').write_text(json.dumps(rows,indent=2))

def xarray_lookup(index,head=0xffff978e81830922):
 trace=[];entry=head
 while entry&3==2 and entry>k.DM:
  va=entry-2;fo=k.p2f(va-k.DM)
  if fo is None:return None,trace
  shift=k.m[fo];slot=(index>>shift)&63
  if shift>63:return None,trace
  entry=struct.unpack_from('<Q',k.m,fo+40+slot*8)[0]
  trace.append({'node':hex(va),'shift':shift,'slot':slot,'entry':hex(entry)})
  if len(trace)>8:return None,trace
 if k.VM<=entry<k.VM+0x10000000:
  return (entry-k.VM)//64*4096,trace
 return None,trace
