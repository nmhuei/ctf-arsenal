from pathlib import Path
import mmap,struct,hashlib,json
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2]
files={
 'collector':{'words':[-1230090044,2127323314,-1059689052,1415825335,-2074817314,253067825,763488977,855944017],'size':23360,'magic':b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00','expected_sha256':'9ec3d41b5db1baee571dbe1bebff4774b85d61e046edce96a86dd489644ce2e7'},
 'agent':{'words':[1911406995,143388708,2090053735,-241604588,2083559575,123805934,-1519948683,1819491038],'size':65408,'magic':b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'},
 'archive':{'words':[2032387434,2144802918,1612300407,-1744597057,376328228,-333502917,137095450,-350496053],'size':2*1024*1024,'magic':b'PK\x03\x04'},
}
results=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for name,info in files.items():
  words=[x&0xffffffff for x in info['words']]
  key=struct.pack('>4I',*(words[i]^words[i+4] for i in range(4)))
  iv=struct.pack('>4I',words[4],words[5],0,0)
  def cipher():return AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=int.from_bytes(iv,'big'))
  signature=cipher().encrypt(info['magic']);start=0;count=0
  while True:
   start=m.find(signature,start)
   if start<0:break
   count+=1;plain=cipher().decrypt(m[start:start+info['size']]);sha=hashlib.sha256(plain).hexdigest()
   path=root/f'script/offline_audit/mega_{name}_{start:x}.bin';path.write_bytes(plain)
   row={'kind':name,'offset':hex(start),'size':len(plain),'sha256':sha,'file':str(path.relative_to(root)),'head':plain[:64].hex()};results.append(row);print(row,flush=True)
   start+=len(signature)
  print(name,'ciphertext signature matches',count,flush=True)
(root/'script/offline_audit/mega_buffer_results.json').write_text(json.dumps(results,indent=2))
