from pathlib import Path
import mmap,struct,zlib,hashlib,json
root=Path(__file__).resolve().parents[2];out=root/'script/offline_audit/png';out.mkdir(exist_ok=True)
report=[];seen=set();count=0
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 pos=0
 while True:
  pos=m.find(b'\x89PNG\r\n\x1a\n',pos)
  if pos<0:break
  start=pos;pos+=8;count+=1
  if m[start+12:start+16]!=b'IHDR':continue
  width,height=struct.unpack('>II',m[start+16:start+24])
  if not (500<=width<=10000 and 300<=height<=10000):continue
  cursor=start+8;valid=True
  for _ in range(10000):
   if cursor+12>len(m):valid=False;break
   length=struct.unpack('>I',m[cursor:cursor+4])[0];typ=m[cursor+4:cursor+8]
   if length>20000000 or cursor+12+length>len(m):valid=False;break
   crc=struct.unpack('>I',m[cursor+8+length:cursor+12+length])[0]
   if zlib.crc32(m[cursor+4:cursor+8+length])!=crc:valid=False;break
   cursor+=12+length
   if typ==b'IEND':break
  else:valid=False
  row={'offset':hex(start),'width':width,'height':height,'valid':valid,'bytes':cursor-start}
  if valid:
   b=m[start:cursor];sha=hashlib.sha256(b).hexdigest();row['sha256']=sha
   if sha not in seen:
    name=f'{start:x}_{width}x{height}.png';(out/name).write_bytes(b);row['file']=name;seen.add(sha)
    print('carved',name,len(b),flush=True)
  report.append(row)
(root/'script/offline_audit/png_report.json').write_text(json.dumps({'signatures':count,'candidates':report},indent=2))
print('PNG signatures',count,'large candidates',len(report),'unique valid',len(seen),flush=True)
