from pathlib import Path
import sys,json,struct,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from recover_archive_central import crypt
raw=(P/'small_derived_archive.zip').read_bytes();records=json.loads((H/'archive_central_records.json').read_text());sigmap={}
for i in range(32,36):
 r=records[i];start=r['local_offset']+30+len(r['name']);end=start+r['compressed_size']
 for off in range(start,end-8,8):
  for layer in ('zip','mega'):
   sig=raw[off:off+8];sig=sig if layer=='zip' else crypt(sig,off)
   if b'\n' not in sig:sigmap[sig]=(off,layer)
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap)
r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*8,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr;res=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for l in r.stdout.splitlines():
  pos=int(l.split(b':')[0]);logical,layer=sigmap[m[pos:pos+8]];res.append({'memory':hex(pos),'logical':logical,'layer':layer})
(P/'small_short_signature_hits.json').write_text(json.dumps(res,indent=2));print('SIGNATURES',len(sigmap),'HITS',res)
