import kernel_walk as k,json,zlib
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');patterns={'schema16':'{"schemaVersion":33'.encode('utf-16le'),'altrows':b':3\t0\t'};rows=[]
for label,sig in patterns.items():
 pos=0;hits=[]
 while True:
  pos=k.m.find(sig,pos)
  if pos<0:break
  hit=pos;pos+=1;hits.append(hex(hit))
 print(label,len(hits),hits[:30],flush=True);rows.append({'label':label,'hits':hits})
(OUT/'short_profile_hits.json').write_text(json.dumps(rows,indent=2))
