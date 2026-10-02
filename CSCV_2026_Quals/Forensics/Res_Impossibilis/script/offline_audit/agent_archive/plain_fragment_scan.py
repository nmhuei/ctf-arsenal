from pathlib import Path
import subprocess,mmap,json
P=Path(__file__).resolve().parent;H=P.parent;sigmap={}
for fname,start in [('27_extensions.partial.json',0),('27_extensions.tail.json',35265)]:
 d=(P/fname).read_bytes()
 for i in range(0,len(d)-64,1024):sigmap[d[i:i+64]]=(start+i,'extensions-utf8')
 for i in [max(0,len(d)-64),max(0,len(d)-256)]:sigmap[d[i:i+64]]=(start+i,'extensions-utf8')
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap if b'\n' not in s)
r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*64,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr;results=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for l in r.stdout.splitlines():
  off=int(l.split(b':')[0]);logical,kind=sigmap[m[off:off+64]];results.append({'memory':hex(off),'logical_plaintext':logical,'kind':kind})
(P/'plain_fragment_hits.json').write_text(json.dumps(results,indent=2));print(results)
