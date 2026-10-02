from pathlib import Path
import mmap,struct,json,subprocess
OUT=Path('script/offline_audit/agent_collector'); DM=0xffff978e40000000; VM=0xffffe18300000000
f=open('script/evidence/mem.clean','rb');m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
segs=[];o=0
while o<len(m):
 magic,ver,s,e,r=struct.unpack_from('<IIQQQ',m,o);assert magic==0x4c694d45
 segs.append((s,e+1,o+32));o+=32+e-s+1

def p2f(p):
 for s,e,f in segs:
  if s<=p<e:return f+p-s

def f2p(o):
 for s,e,f in segs:
  if f<=o<f+e-s:return s+o-f

def qp(p):
 o=p2f(p)
 return struct.unpack_from('<Q',m,o)[0] if o is not None else 0

def parents(p):
 pat='[\\x01-\\xff][\\x%02x-\\x%02x]'%((p>>8)&0xf0,((p>>8)&0xf0)+15)+''.join('\\x%02x'%c for c in struct.pack('<Q',p)[2:7])+r'[\x00\x80]'
 proc=subprocess.run(['rg','-aob','--no-unicode',pat,'script/evidence/mem.clean'],capture_output=True)
 rows=[]
 for line in proc.stdout.splitlines():
  if b':' not in line:continue
  o=int(line.split(b':',1)[0]);phys=f2p(o)
  if phys%8:continue
  v=struct.unpack_from('<Q',m,o)[0]
  if v&1 and (v&0xffffffffff000)==p:
   rows.append((phys, v))
 return rows

def walk(root,va):
 cur=root
 for shift in [39,30,21,12]:
  e=qp(cur+((va>>shift)&511)*8)
  if not e&1:return None
  cur=e&0xffffffffff000
  if shift in [30,21] and e&128:return (cur&~((1<<shift)-1))+(va&((1<<shift)-1))
 return cur+(va&4095)

if __name__=='__main__':
 levels=[0x10158a000];allrows=[]
 for lev in range(3):
  nexts=set()
  for target in levels:
   ps=parents(target);print('level',lev,'child',hex(target),'parents',[(hex(x),hex(v)) for x,v in ps],flush=True)
   allrows.append({'level':lev,'child':hex(target),'parents':[[hex(x),hex(v)] for x,v in ps]})
   for p,v in ps:
    if p%4096 == (((DM+0x2f71a000)>>[21,30,39][lev])&511)*8: nexts.add(p&~4095)
  levels=list(nexts)
  if len(levels)>20: print('too many');break
 roots=[]
 for root in levels:
  if walk(root,DM+0x2f71a000)==0x2f71a000:
   print('ROOT',hex(root),flush=True);roots.append(root)
 (OUT/'kernel_roots.json').write_text(json.dumps({'walk':allrows,'roots':roots},indent=2))
 for root in roots[:1]:
  for pa in [0x2f71a000,0x34081000,0x317cb000,0x35136000,0x35137000,0x35138000,0x3513a000]:
   va=VM+(pa>>12)*64;p=walk(root,va);print('page',hex(pa),'structVA',hex(va),'structPA',hex(p) if p else None,'bytes',m[p2f(p):p2f(p)+64].hex() if p else None)
