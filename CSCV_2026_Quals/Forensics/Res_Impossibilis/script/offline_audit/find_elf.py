from pathlib import Path
import mmap,struct,json,hashlib
root=Path(__file__).resolve().parents[2]
items=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 p=0;count=0
 while True:
  p=m.find(b'\x7fELF\x02\x01\x01',p)
  if p<0:break
  start=p;p+=7;count+=1
  header=m[start:start+64]
  if len(header)<64:continue
  vals=struct.unpack('<16sHHIQQQIHHHHHH',header)
  _,typ,mach,ver,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr=vals
  if typ not in (2,3) or mach!=62 or ehsize!=64:continue
  if not (0<shoff<200000 and 0<shnum<80 and shsize==64):continue
  total=shoff+shsize*shnum
  image=m[start:start+total]
  if b'gethostname' in image and b'srand' in image and b'readdir' in image:
   path=root/f'script/offline_audit/elf_{start:x}.bin';path.write_bytes(image)
   row={'offset':hex(start),'size':total,'entry':hex(entry),'file':str(path.relative_to(root)),'sha256':hashlib.sha256(image).hexdigest()};items.append(row)
   print(row,flush=True)
(root/'script/offline_audit/elf_candidates.json').write_text(json.dumps({'elf_signatures':count,'candidates':items},indent=2))
print('signatures',count,'filtered',len(items),flush=True)
