from pathlib import Path
import struct,json
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2];b=(root/'script/offline_audit/tls75_server.bin').read_bytes();records=[];pos=0
while pos+5<len(b):
 n=int.from_bytes(b[pos+3:pos+5],'big');records.append((pos,b[pos:pos+5],b[pos+5:pos+5+n]));pos+=5+n
rows=[s.split('\t') for s in (root/'script/offline_audit/aes_scan/aes_keys.txt').read_text().splitlines() if not s.startswith('#')];keys={bytes.fromhex(r[1]):r[0] for r in rows}
for key,where in list(keys.items()):
 keys[b''.join(key[i:i+4][::-1] for i in range(0,len(key),4))]=where
 keys[key[::-1]]=where
prefixes=[b'HTTP/1.1 200 OK\r\n',b'HTTP/1.1 206 Par',b'HTTP/1.1 404 Not ',b'HTTP/1.1 302 Fou']
for key,where in keys.items():
 for pos,aad,data in records:
  if aad[0]!=23:continue
  for prefix in prefixes:
   if len(prefix)!=16:continue
   counter=AES.new(key,AES.MODE_ECB).decrypt(bytes(x^y for x,y in zip(data[:16],prefix)))
   if counter[-4:]!=b'\0\0\0\2':continue
   nonce=counter[:12];c=AES.new(key,AES.MODE_GCM,nonce=nonce);c.update(aad)
   try:p=c.decrypt_and_verify(data[:-16],data[-16:])
   except ValueError:continue
   result={'memory_offset':where,'key':key.hex(),'record_offset':pos,'nonce':nonce.hex(),'plaintext_head':p[:200].decode(errors='replace')};print(result,flush=True)
   (root/'script/offline_audit/tls75_key.json').write_text(json.dumps(result,indent=2));(root/'script/offline_audit/tls75_http_first.bin').write_bytes(p)
print('tested keys',len(keys),flush=True)
