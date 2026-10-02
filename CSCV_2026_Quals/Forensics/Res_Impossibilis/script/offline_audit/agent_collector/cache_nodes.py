import kernel_walk as k,struct,json,numpy as np
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');ARRAY=0xffff978f4c1d6f00

def readnode(va):
 fo=k.p2f(va-k.DM)
 if fo is None:return None
 b=k.m[fo:fo+552]
 if len(b)!=552:return None
 shift,off,count,nr=b[:4]
 par,arr,nex,prev=struct.unpack_from('<4Q',b,8)
 if arr!=ARRAY or shift%6 or shift>54 or nex!=va+24 or prev!=va+24:return None
 return (shift,off,par,struct.unpack_from('<64Q',b,40))

if __name__=='__main__':
 sig=struct.pack('<Q',ARRAY);pos=0;nodes={};total=0
 while True:
  pos=k.m.find(sig,pos)
  if pos<0:break
  fo=pos-16;pos+=1;total+=1;pa=k.f2p(fo)
  if pa is None:continue
  va=k.DM+pa;n=readnode(va)
  if n:nodes[va]=n
 print('array references',total,'valid selflinked nodes',len(nodes),flush=True)
 rows=[];fail=0;roots=set()
 for va,n in nodes.items():
  shift,off,par,slots=n
  if shift:continue
  base=0;current=va;seen=set();okay=True
  while nodes.get(current) and nodes[current][2]:
   if current in seen:okay=False;break
   seen.add(current);node=nodes[current];parent=nodes.get(node[2]) or readnode(node[2])
   if parent is None or parent[0]!=node[0]+6:okay=False;break
   base+=node[1]<<parent[0];current=node[2]
  if not okay:fail+=1;continue
  roots.add(current)
  for i,entry in enumerate(slots):
   if k.VM<=entry<k.VM+0x10000000 and entry%64==0:
    pa=(entry-k.VM)//64*4096
    rows.append((base+i,pa,va))
 idx=np.array(rows,dtype=np.uint64);idx=idx[np.argsort(idx[:,0])]
 np.save(OUT/'dump_cache_node_index.npy',idx)
 (OUT/'dump_cache_nodes.json').write_text(json.dumps({hex(v):[n[0],n[1],hex(n[2])] for v,n in nodes.items()}))
 print('leaf failures',fail,'cache entries',len(idx),'indexrange',idx[0,0],idx[-1,0],'roots',[hex(v) for v in roots])
