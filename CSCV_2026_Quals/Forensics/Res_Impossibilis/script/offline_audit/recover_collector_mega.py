from pathlib import Path
import mmap, struct, hashlib, json
from Crypto.Cipher import AES

ROOT=Path(__file__).resolve().parents[2]
MEM=ROOT/"script/evidence/mem.clean"
raw_words=[-1230090044,2127323314,-1059689052,1415825335,-2074817314,253067825,763488977,855944017]
w=[x&0xffffffff for x in raw_words]
key=struct.pack(">4I",*(w[i]^w[i+4] for i in range(4)))
iv_int=int.from_bytes(struct.pack(">4I",w[4],w[5],0,0),"big")
expected="9ec3d41b5db1baee571dbe1bebff4774b85d61e046edce96a86dd489644ce2e7"
size=23360
plain0=bytes.fromhex("7f454c46020101000000000000000000")
ks=AES.new(key,AES.MODE_CTR,nonce=b"",initial_value=iv_int).encrypt(b"\0"*16)
sig=bytes(a^b for a,b in zip(plain0,ks))
print("key",key.hex(),"iv",hex(iv_int),"cipher_sig",sig.hex(),flush=True)

rows=[]
with MEM.open("rb") as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
    pos=0
    while True:
        hit=m.find(sig,pos)
        if hit<0:break
        pos=hit+1
        ct=m[hit:hit+size]
        if len(ct)<size:continue
        pt=AES.new(key,AES.MODE_CTR,nonce=b"",initial_value=iv_int).decrypt(ct)
        h=hashlib.sha256(pt).hexdigest()
        row={"offset":hex(hit),"sha256":h,"elf":pt[:4]==b"\x7fELF","size":len(pt)}
        rows.append(row)
        print(row,flush=True)
        if h==expected:
            out=ROOT/"script/offline_audit/sys_audit_collector.recovered"
            out.write_bytes(pt)
            print("MATCH",out,flush=True)
            break
(ROOT/"script/offline_audit/collector_mega_cipher_hits.json").write_text(json.dumps(rows,indent=2))
