import json,itertools
from pathlib import Path
from hash_model import hkey
OUT=Path('script/offline_audit/agent_collector/alt_reconstruction');lines=Path('script/offline_audit/root_files/37_AlternateServices.partial.txt').read_text().splitlines()[1:];knownkeys={l.split('\t')[0] for l in lines};knownslots={18,20,24,27,28,29,33,35,36,39,42,44,45,47,50,51,52,53,56,60,61}
observed=set(json.loads((OUT/'pcap_domains.json').read_text()))|{k.split(':')[1] for k in knownkeys}
extra={'firefox.settings.services.mozilla.com','aus5.mozilla.org','accounts.google.com','www.googletagservices.com','adservice.google.com','ssl.gstatic.com','www.mozilla.org','addons.mozilla.org'}
hosts=sorted(h for h in observed|extra if any(h.endswith(s) for s in ['google.com','google.com.vn','googleapis.com','gstatic.com','youtube.com','googlevideo.com','doubleclick.net','googlesyndication.com','google-analytics.com','googleadservices.com','googletagmanager.com','googletagservices.com','ggpht.com','ytimg.com','mozilla.org','mozilla.net','mozgcp.net','facebook.com','facebook.net','coccoc.com','transcend-cdn.com']))
def record(host,attr,expiry=1791432442):
 return f'https:{host}:443:.:{attr}:3\t0\t20704\thttps:{host}:443:{host}:443::n:{expiry}:h3:y:1788840424:n:{attr}:|n:y:\n'
attrs=['^partitionKey=%28https%2Cgoogle.com%29','^partitionKey=%28https%2Ccoccoc.com%29','^partitionKey=%28https%2Cmozilla.org%29','']
rows=[]
for host,attr in itertools.product(hosts,attrs):
 r=record(host,attr);key=r.split('\t')[0]
 if key in knownkeys:continue
 h=hkey(key);probe=[((h>>26)-j*((h&63)|1))&63 for j in range(64)];first=next(p for p in probe if p not in knownslots)
 if first>=18:continue
 rows.append({'host':host,'attr':attr,'key':key,'length':len(r),'probe':probe,'observed_host':host in observed})
solutions=[]
for n in [3,4,5]:
 # Enumerate actual low bucket sets. Known analytics record requires bucket2 occupied.
 ns=0
 for low in itertools.combinations(range(18),n):
  if 2 not in low:continue
  occupied=knownslots|set(low);options=[]
  for slot in low:
   opts=[]
   for row in rows:
    reachable=[]
    for p in row['probe']:
     if p not in occupied:break
     if p==slot:opts.append(row);break
   if slot==low[-1]:opts=[r for r in opts if r['attr']==attrs[1]]
   options.append(opts)
  if any(not x for x in options):continue
  def search(i,selected,total,keys):
   if i==n:
    if total==747:
     solutions.append({'n':n,'slots':low,'records':[{k:v for k,v in r.items() if k!='probe'} for r in selected]})
    return
   remains=options[i+1:]
   minleft=sum(min(r['length'] for r in rs) for rs in remains);maxleft=sum(max(r['length'] for r in rs) for rs in remains)
   for row in options[i]:
    new=total+row['length']
    if row['key'] in keys or new+minleft>747 or new+maxleft<747:continue
    search(i+1,selected+[row],new,keys|{row['key']})
  search(0,[],0,set())
 print('n',n,'cumulative solutions',len(solutions),flush=True)
 # Keep bounded enumeration; 5 records tested only if earlier hypotheses empty.
 if solutions:break
(OUT/'record_hypotheses.json').write_text(json.dumps(solutions,indent=2));print('candidates',len(rows),'total',len(solutions))
for r in solutions[:20]:print(r['slots'],[(x['host'],x['attr']) for x in r['records']])
