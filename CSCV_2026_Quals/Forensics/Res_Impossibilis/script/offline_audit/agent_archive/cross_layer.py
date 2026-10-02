from pathlib import Path
import json,struct,sys,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from recover_archive_central import crypt
raw=(P/'pte_archive.zip').read_bytes();known=(P/'pte_known.bin').read_bytes();sigmap={}
for align in (-20,-48,-21):
 for j in range(17):
  base=align+j*4096
  for layer in ('zip','mega'):
   for shift in range(20):
    lo=max(0,base)+shift
    if lo+16>len(raw) or not all(known[lo:lo+16]):break
    sig=raw[lo:lo+16] if layer=='zip' else crypt(raw[lo:lo+16],lo)
    if b'\n' not in sig:
     sigmap.setdefault(sig,[]).append((lo,layer));break
pat='|'.join(''.join(f'\\x{b:02x}' for b in sig) for sig in sigmap)
r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*16,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr;(P/'cross_hits.txt').write_bytes(r.stdout)
results=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 segs=[];o=0
 while o<len(m):
  _,_,s,e,_=struct.unpack_from('<IIQQQ',m,o);segs.append((s,e+1,o+32));o+=32+e-s+1
 def f2p(x):
  for s,e,fo in segs:
   if fo<=x<fo+e-s:return s+x-fo
 for l in r.stdout.splitlines():
  hit=int(l.split(b':')[0]); sig=m[hit:hit+16]
  if sig not in sigmap:continue
  for logical,layer in sigmap[sig]:
   within=f2p(hit)%4096;fo=hit-within;lb=logical-within;lo=max(lb,0);hi=min(lb+4096,len(raw));data=m[fo+lo-lb:fo+hi-lb];data=data if layer=='zip' else crypt(data,lo)
   conflicts=sum(1 for i,b in enumerate(data,lo) if known[i] and raw[i]!=b);new=sum(1 for i in range(lo,hi) if not known[i]);row={'memory':hex(fo),'logical':lb,'layer':layer,'conflicts':conflicts,'new':new}
   if row not in results:
    results.append(row)
    if new:print(row,flush=True)
    if new and not conflicts:(P/f'cross_{layer}_{fo:x}_{lo}.bin').write_bytes(data)
(P/'cross_results.json').write_text(json.dumps(results,indent=2));print('HITS',len(r.stdout.splitlines()),'PAGES',len(results))
