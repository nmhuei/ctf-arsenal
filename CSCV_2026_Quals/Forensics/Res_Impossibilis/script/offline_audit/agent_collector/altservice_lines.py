import kernel_walk as k,json
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');sig=b'\t0\t20704\t';pos=0;rows=[]
while True:
 pos=k.m.find(sig,pos)
 if pos<0:break
 hit=pos;pos+=1
 left=max(k.m.rfind(b'\n',max(0,hit-1000),hit),k.m.rfind(b'\0',max(0,hit-1000),hit))+1
 right=k.m.find(b'\n',hit,hit+2000)
 if right<0:continue
 line=k.m[left:right+1]
 if not line.startswith(b'https:') or not all(c in b'\t\n\r' or 32<=c<127 for c in line):continue
 rows.append({'file':hex(left),'line':line.decode()})
(OUT/'altservice_lines.json').write_text(json.dumps(rows,indent=2));print('hits',len(rows),'unique',len(set(r['line'] for r in rows)))
for r in rows:print(r['file'],r['line'].strip())
