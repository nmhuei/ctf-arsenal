from pathlib import Path
import mmap, subprocess, json,zlib,struct,sys
P=Path(__file__).resolve().parent; H=P.parent; MEM=H.parent/'evidence/mem.clean'
records=json.loads((H/'archive_central_records.json').read_text())
sigs=[b'PK\x03\x04\x14\0\x01\0\0\0\0\x68\x21\x55',b'[CryptoEngine]',b'{"schemaVersion":',b'{"doh-rollout@mozilla.org"',b'library=',b'"external_update_url"',b'{"created":',b'{"startupInterrupted":',b'{"version":',b'text/plain',b'application/json',b'# TLS 1.3 Key Log File']
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigs)
if not (P/'plain_hits_correct.txt').exists():
 r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--regexp',pat,str(MEM)],capture_output=True);assert r.returncode in (0,1),r.stderr;(P/'plain_hits_correct.txt').write_bytes(r.stdout)
hits=[int(l.split(b':')[0]) for l in (P/'plain_hits_correct.txt').read_bytes().splitlines()]; print('hits',len(hits),flush=True)
results=[]; prefixes=[]
with MEM.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for hit in hits:
  si=next((s for s in sigs if m[hit:hit+len(s)]==s),b'')
  if si.startswith(b'PK'): print('CLEARZIP',hex(hit),flush=True)
  if si in [b'[CryptoEngine]',b'{"schemaVersion":',b'{"doh-rollout@mozilla.org"']:
   prefixes.append({'offset':hex(hit),'signature':si.decode(),'prefix':m[hit:hit+150].decode(errors='replace')})
  for shift in range(-2,25):
   pos=hit+shift
   for i,r in enumerate(records):
    size=r['plain_size']; data=m[pos:pos+size]
    if zlib.crc32(data)==int(r['crc32'],16):
     out=P/f'{i:02d}_{Path(r["name"]).name}';out.write_bytes(data)
     row={'index':i,'offset':hex(pos),'crc32':r['crc32'],'size':size,'file':out.name}
     if row not in results:results.append(row);print(row,flush=True)
(P/'plain_recoveries.json').write_text(json.dumps(results,indent=2));(P/'plain_prefixes.json').write_text(json.dumps(prefixes,indent=2))
