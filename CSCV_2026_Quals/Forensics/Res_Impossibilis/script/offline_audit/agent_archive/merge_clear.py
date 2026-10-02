from pathlib import Path
import mmap,struct,json,sys,zlib
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import decrypt
records=json.loads((H/'archive_central_records.json').read_text());raw=bytearray((H/'archive_from_central.zip').read_bytes());known=bytearray((H/'archive_from_central_known.bin').read_bytes());pages=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 segs=[];o=0
 while o<len(m):
  magic,ver,s,e,res=struct.unpack_from('<IIQQQ',m,o);assert magic==0x4c694d45;segs.append((s,e+1,o+32));o+=32+e-s+1
 def f2p(x):
  for s,e,fo in segs:
   if fo<=x<fo+e-s:return s+x-fo
 for l in (P/'plain_hits.txt').read_bytes().splitlines():
  hit=int(l.split(b':')[0])
  if m[hit:hit+4]!=b'PK\x03\x04':continue
  h=struct.unpack_from('<4s5H3I2H',m,hit); name=m[hit+30:hit+30+h[9]].decode(errors='replace')
  matches=[(i,r) for i,r in enumerate(records) if r['name']==name and int(r['crc32'],16)==h[6] and r['compressed_size']==h[7]]
  for i,r in matches:
   within=f2p(hit)%4096;base=hit-within;lb=r['local_offset']-within;lo=max(lb,0);hi=min(lb+4096,len(raw));data=m[base+lo-lb:base+hi-lb]
   conflicts=[j for j,b in enumerate(data,lo) if known[j] and raw[j]!=b]
   print('HEADER',i,hex(hit),name,'page_logical',lb,'conflicts',len(conflicts),flush=True)
   if conflicts:continue
   raw[lo:hi]=data;known[lo:hi]=b'\x01'*(hi-lo);pages.append({'memory':hex(base),'logical':lb,'entry':i,'source':'clear_zip'})
results=[]
for i,r in enumerate(records):
 o=r['local_offset']; row=dict(r,index=i,complete=False)
 if all(known[o:o+30]):
  h=struct.unpack_from('<4s5H3I2H',raw,o);assert h[0]==b'PK\x03\x04'; start=o+30+h[9]+h[10];end=start+h[7]
  if all(known[o:end]):
   p=decrypt(raw[start:end])[12:];valid=zlib.crc32(p)==h[6] and len(p)==h[8]; row['complete']=valid
   print('ENTRY',i,valid,r['name'],flush=True)
   if valid:(P/f'{i:02d}_{Path(r["name"]).name}').write_bytes(p)
 results.append(row)
(P/'merged_archive.zip').write_bytes(raw);(P/'merged_known.bin').write_bytes(known);report={'known':sum(known),'pages':pages,'entries':results};(P/'merged_report.json').write_text(json.dumps(report,indent=2));print('TOTAL',sum(known),'COMPLETE',sum(r['complete'] for r in results))
