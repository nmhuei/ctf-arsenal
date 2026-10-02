from pathlib import Path
import mmap,re,json
root=Path(__file__).resolve().parents[2]
labels=[b'CLIENT_RANDOM',b'CLIENT_EARLY_TRAFFIC_SECRET',b'CLIENT_HANDSHAKE_TRAFFIC_SECRET',b'SERVER_HANDSHAKE_TRAFFIC_SECRET',b'CLIENT_TRAFFIC_SECRET_0',b'SERVER_TRAFFIC_SECRET_0',b'EXPORTER_SECRET']
keys=set();hits={}
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for label in labels:
  start=0;n=0
  while True:
   start=m.find(label+b' ',start)
   if start<0:break
   match=re.match(rb'([A-Z_0-9]+) ([0-9a-fA-F]{64}) ([0-9a-fA-F]{64,128})(?![0-9a-fA-F])',m[start:start+280])
   if match:keys.add(match.group(0).decode());n+=1
   start+=len(label)+1
  hits[label.decode()]=n
(root/'script/offline_audit/tls_keys.log').write_text('\n'.join(sorted(keys))+'\n')
(root/'script/offline_audit/tls_key_counts.json').write_text(json.dumps({'occurrences':hits,'unique_records':len(keys)},indent=2))
print('unique key records',len(keys),'occurrences',hits,flush=True)
