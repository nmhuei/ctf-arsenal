from pathlib import Path
import mmap,re,json
root=Path(__file__).resolve().parents[2]
lines=(root/'script/offline_audit/collector_stream75.txt').read_text().splitlines();client=bytearray();server=bytearray()
for line in lines:
 if re.fullmatch(r'\t?[0-9a-f]+',line):
  (server if line.startswith('\t') else client).extend(bytes.fromhex(line.strip()))
(root/'script/offline_audit/tls75_client.bin').write_bytes(client);(root/'script/offline_audit/tls75_server.bin').write_bytes(server)
print('stream bytes',len(client),len(server),flush=True)
needles={'client_random':bytes(client[11:43]),'server_random':bytes(server[11:43]),'session_id':bytes(client[44:76])}
out={}
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for name,sig in needles.items():
  p=0;rows=[]
  while True:
   p=m.find(sig,p)
   if p<0:break
   row={'offset':hex(p),'context':m[max(0,p-128):p+512].hex()};rows.append(row);print(name,hex(p),flush=True)
   (root/f'script/offline_audit/tls_context_{p:x}.bin').write_bytes(m[max(0,p-8192):p+8192]);p+=len(sig)
  out[name]={'signature':sig.hex(),'hits':rows}
(root/'script/offline_audit/tls75_memory.json').write_text(json.dumps(out,indent=2))
