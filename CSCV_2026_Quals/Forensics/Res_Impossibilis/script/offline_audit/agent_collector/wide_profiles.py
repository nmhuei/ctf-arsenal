from pathlib import Path
import kernel_walk as k,zlib,json
OUT=Path('script/offline_audit/agent_collector');prefix=Path('script/offline_audit/agent_archive/27_extensions.partial.json').read_bytes()[:96].decode();tail=(OUT/'candidate_extensions.json').read_bytes()[-719:].decode()
patterns={'prefix_utf16':prefix.encode('utf-16le'),'tail_utf16':tail[:64].encode('utf-16le'),'alternate_utf16':(OUT/'candidate_AlternateServices.txt').read_bytes()[4096:4160].decode().encode('utf-16le')};rows=[]
for name,sig in patterns.items():
 pos=0;hits=[]
 while True:
  pos=k.m.find(sig,pos)
  if pos<0:break
  hit=pos;pos+=1;hits.append(hex(hit))
  if name=='prefix_utf16':
   blob=k.m[hit:hit+37583*2]
   try:
    s=blob.decode('utf-16le'); j=s.find('\0');s=s[:j] if j>=0 else s
    for end in [s.find('"location":"app-builtin"}]}')+len('"location":"app-builtin"}]}'),len(s)]:
     b=s[:end].encode()
     if len(b)==37583 and zlib.crc32(b)==0x20a2f078:(OUT/'recovered_files/extensions.json').write_bytes(b);print('VERIFIED',hex(hit))
   except UnicodeError:pass
 rows.append({'pattern':name,'hits':hits});print(name,len(hits),hits[:20],flush=True)
(OUT/'wide_profile_hits.json').write_text(json.dumps(rows,indent=2))
