import kernel_walk as k,struct,json,subprocess,re
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');NAMES=['extensions.json','AlternateServices.txt','handlers.json','SiteSecurityServiceState.txt']

def q(va,off=0):
 fo=k.p2f(va-k.DM+off)
 return struct.unpack_from('<Q',k.m,fo)[0] if fo is not None else 0

def name(va):
 fo=k.p2f(va-k.DM)
 if fo is None:return '?'
 length=struct.unpack_from('<I',k.m,fo+0x24)[0];nv=q(va,0x28);nf=k.p2f(nv-k.DM)
 if length>512 or nf is None:return '?'
 return bytes(k.m[nf:nf+length]).decode(errors='replace')

def path(va):
 parts=[];seen=set()
 for _ in range(25):
  if va in seen:break
  seen.add(va);parts.append(name(va));par=q(va,0x18)
  if not par or par==va:break
  va=par
 return '/'.join(reversed(parts))

if __name__=='__main__':
 p=subprocess.run(['rg','-aob','--no-unicode','|'.join(re.escape(n) for n in NAMES),'script/evidence/mem.clean'],capture_output=True)
 rows=[]
 for l in p.stdout.splitlines():
  if b':' not in l:continue
  off,b=l.split(b':',1);off=int(off);dfo=off-0x38;pa=k.f2p(dfo)
  if pa is None:continue
  va=k.DM+pa;length=struct.unpack_from('<I',k.m,dfo+0x24)[0]
  if length!=len(b) or q(va,0x28)!=va+0x38:continue
  inode=q(va,0x30);row={'dentry':hex(va),'namefile':hex(off),'path':path(va),'inode':hex(inode)}
  if inode:
   fo=k.p2f(inode-k.DM)
   if fo is not None:
    row.update(size=q(inode,0x50),mapping=hex(q(inode,0x30)),head=hex(q(q(inode,0x30),0x10)))
  rows.append(row);print(row)
 (OUT/'profile_inodes.json').write_text(json.dumps(rows,indent=2))
