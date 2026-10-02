import kernel_walk as k,profile_inodes as pi,json,struct
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');root=pi.q(0xffff978f8a820480,0x18);rows=[]

def children(parent,path,depth):
 head=parent+0xa0;cur=pi.q(head);seen=set()
 while cur and cur!=head and cur not in seen and len(seen)<1000:
  seen.add(cur);d=cur-0x90;parent_check=pi.q(d,0x18);nm=pi.name(d)
  if parent_check!=parent or nm=='?':break
  ino=pi.q(d,0x30);fo=k.p2f(ino-k.DM) if ino else None;mode=struct.unpack_from('<H',k.m,fo)[0] if fo is not None else 0;mapping=pi.q(ino,0x30) if ino else 0
  row={'dentry':hex(d),'path':path+'/'+nm,'inode':hex(ino),'mode':hex(mode),'size':pi.q(ino,0x50) if ino else 0,'mapping':hex(mapping),'head':hex(pi.q(mapping,0x10)) if mapping else '0x0'};rows.append(row)
  if mode&0xf000==0x4000 and depth<2:children(d,path+'/'+nm,depth+1)
  cur=pi.q(cur)
children(root,'/tmp/firefox-clean',0)
(OUT/'profile_dentry_listing.json').write_text(json.dumps(rows,indent=2));print('parent',hex(root),'entries',len(rows))
for r in rows:
 if any(x in r['path'] for x in ['lock','sessionstore','recovery','search','Startup','extensions.json']):print(r)
