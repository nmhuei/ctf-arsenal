import kernel_walk as k,struct,json,zlib
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');rows=[]
for name,size,logical,crc in [('extensions.json',37583,36864,0x20a2f078),('AlternateServices.txt',5398,4096,0x25489b76)]:
 candidate=(OUT/f'candidate_{name}').read_bytes();sig=candidate[logical:logical+64];pos=0;hits=[]
 while True:
  pos=k.m.find(sig,pos)
  if pos<0:break
  hit=pos;pos+=1;start=hit-logical
  blob=k.m[start:start+size];okay=zlib.crc32(blob)==crc
  hitrow={'file':hex(hit),'inferred_start':hex(start),'whole_crc_match':okay};hits.append(hitrow)
  if okay:(OUT/'recovered_files'/name).write_bytes(blob)
 rows.append({'name':name,'hits':hits});print(name,'hits',len(hits),'offsets',[h['file'] for h in hits],'verified',any(h['whole_crc_match'] for h in hits))
(OUT/'profile_copy_hits.json').write_text(json.dumps(rows,indent=2))
