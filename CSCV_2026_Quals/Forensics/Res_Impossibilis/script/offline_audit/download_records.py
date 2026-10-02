from pathlib import Path
import mmap,json,re
root=Path(__file__).resolve().parents[2]
def varint(b,p):
 n=0
 for shift in range(0,70,7):
  v=b[p];p+=1;n|=(v&127)<<shift
  if not v&128:return n,p
 raise ValueError('varint')
def parse(b):
 fields={};p=0
 while p<len(b):
  key,p=varint(b,p);num,wire=key>>3,key&7
  if not num:raise ValueError('field0')
  if wire==0:v,p=varint(b,p)
  elif wire==2:
   size,p=varint(b,p)
   if p+size>len(b):raise ValueError('length')
   v=b[p:p+size];p+=size
  elif wire in (1,5):size=8 if wire==1 else 4;v=b[p:p+size];p+=size
  else:raise ValueError('wire')
  fields.setdefault(num,[]).append(v)
 return fields
out=[];seen=set()
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 p=0
 while True:
  p=m.find(b'sys_audit_collector',p)
  if p<0:break
  base=max(0,p-650);region=m[base:p+600];p+=len(b'sys_audit_collector')
  for start in range(min(650,len(region))):
   try:
    if region[start]!=10:continue
    size,head=varint(region,start+1)
    if not 100<size<1600 or head+size>len(region):continue
    info=parse(region[head:head+size])
    guid=info.get(1,[b''])[0]
    if not re.fullmatch(rb'[0-9a-f-]{36}',guid):continue
    d=parse(info[4][0]);path=d.get(14,[b''])[0]
    if b'sys_audit_collector' not in path:continue
    digest=d.get(19,[b''])[0]
    row={'offset':hex(base+start),'guid':guid.decode(),'hash':digest.hex(),'hash_bytes':len(digest),'size_total':d.get(10),'size_received':d.get(15),'state':d.get(21),'target_path_hex':path.hex(),'source_url':d.get(4,[b''])[0].decode(errors='replace')}
    key=(row['guid'],row['hash'],str(row['state']))
    if key in seen:continue
    seen.add(key);out.append(row)
    (root/f'script/offline_audit/download_{base+start:x}.protobuf').write_bytes(region[start:head+size])
    print(row,flush=True)
   except (IndexError,ValueError,KeyError,TypeError):continue
(root/'script/offline_audit/download_records.json').write_text(json.dumps(out,indent=2))
print('parsed records',len(out),flush=True)
