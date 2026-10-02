from pathlib import Path
import json,struct,sys,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import INITIAL,TABLE,decrypt;from recover_archive_central import crypt
raw=bytearray((P/'pte_archive.zip').read_bytes());known=(P/'pte_known.bin').read_bytes();template=(P/'extensions_template.json').read_bytes();uuid=template.index(b'00000000-0000-0000-0000-000000000000');r=json.loads((H/'archive_central_records.json').read_text())[27];o=r['local_offset'];start=o+30+len(r['name']);header=decrypt(raw[start:start+12]);a,b,c=INITIAL;encrypted=bytearray()
for p in header+template[:uuid]:
 t=(c&65535)|2;encrypted.append(p^((t*(t^1)>>8)&255));a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255]
assert all(not known[j] or raw[j]==v for j,v in enumerate(encrypted,start));raw[start:start+len(encrypted)]=encrypted;limit=start+len(encrypted);print('UUIDplainoffset',uuid,'cipheroffset',limit,'keysbeforeUUID',hex(a),hex(b),hex(c),flush=True)
sigmap={}
for align in (-20,-48):
 for page in range(8,13):
  for shift in (0,64,1024,2048,3000):
   off=page*4096+align+shift
   if off<35568 or off+32>limit:continue
   for layer in ('zip','mega'):
    sig=bytes(raw[off:off+32]);sig=sig if layer=='zip' else crypt(sig,off)
    if b'\n' not in sig:sigmap[sig]=(off,layer)
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap);rr=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*32,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert rr.returncode in(0,1),rr.stderr
res=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for l in rr.stdout.splitlines():
  pos=int(l.split(b':')[0]);off,layer=sigmap[m[pos:pos+32]];res.append({'memory':hex(pos),'logical':off,'layer':layer})
(P/'rebuilt_extensions_hits.json').write_text(json.dumps({'uuid_plaintext_offset':uuid,'uuid_cipher_offset':limit,'keys_before_uuid':[hex(a),hex(b),hex(c)],'hits':res},indent=2));print('HITS',res)
