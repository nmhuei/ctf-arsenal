from pathlib import Path
import sys,json,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from recover_archive_central import crypt
raw=(P/'near_complete_archive.zip').read_bytes();known=(P/'near_complete_known.bin').read_bytes();sigs={}
for width in (2,4,8):
 for logical in range((53228+width-1)//width*width,55453-32,128):
  assert logical%width==0 and all(known[logical:logical+32])
  for layer in ('zip','mega'):
   data=raw[logical:logical+32];data=data if layer=='zip' else crypt(data,logical);sig=b''.join(data[i:i+width][::-1] for i in range(0,32,width))
   if b'\n' not in sig:sigs[sig]={'logical':logical,'layer':layer,'word_byte_reversal':width}
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigs);r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*32,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr;hits=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for l in r.stdout.splitlines():
  p=int(l.split(b':')[0]);hits.append(dict(sigs[m[p:p+32]],memory=hex(p)))
(P/'word_representation_results.json').write_text(json.dumps({'signatures':len(sigs),'hits':hits},indent=2));print('SIGNATURES',len(sigs),'HITS',hits)
