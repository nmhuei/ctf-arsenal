from pathlib import Path
import mmap,struct,json,subprocess
P=Path(__file__).resolve().parent;H=P.parent;MEM=H.parent/'evidence/mem.clean'
targets=[0x20de1d000,0x20de1e000]
with MEM.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 segs=[];o=0
 while o<len(m):
  magic,ver,s,e,res=struct.unpack_from('<IIQQQ',m,o);segs.append((s,e+1,o+32));o+=32+e-s+1
 def f2p(x):
  for s,e,fo in segs:
   if fo<=x<fo+e-s:return s+x-fo
 def p2f(x):
  for s,e,fo in segs:
   if s<=x<e:return fo+x-s
 for fo in [0x2f3e040,0x2f41040,0x1cd8040,0x1de2040]:targets.append(f2p(fo))
 pat='|'.join(''.join(f'\\x{b:02x}' for b in struct.pack('<Q',t)[2:6]) for t in targets)
 if not (P/'pte_hits_correct.txt').exists():
  r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--regexp',pat,str(MEM)],capture_output=True);assert r.returncode in(0,1),r.stderr;(P/'pte_hits_correct.txt').write_bytes(r.stdout)
 out=[]
 for l in (P/'pte_hits_correct.txt').read_bytes().split(b'\n'):
  if not l:continue
  pos=int(l.split(b':')[0])-2; pp=f2p(pos)
  if pp is None or pp%8:continue
  v=struct.unpack_from('<Q',m,pos)[0];target=v&0xffffffffff000
  if target not in targets or not(v&1):continue
  neighbors=[]
  for i in range(-16,17):
   ep=pos+i*8;e=struct.unpack_from('<Q',m,ep)[0];phy=e&0xffffffffff000;fp=p2f(phy)
   neighbors.append({'i':i,'pte':hex(e),'phys':hex(phy),'file':hex(fp) if fp else None,'sample':m[fp:fp+16].hex() if fp else None})
  row={'target':hex(target),'pte_file':hex(pos),'pte_phys':hex(pp),'neighbors':neighbors};out.append(row);print('PTE',row['target'],row['pte_file'],flush=True)
 (P/'pte_results.json').write_text(json.dumps(out,indent=2));print('CANDIDATES',len(out))
