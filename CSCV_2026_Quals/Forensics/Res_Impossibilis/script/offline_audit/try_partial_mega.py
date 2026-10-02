from pathlib import Path
import struct,hashlib
from Crypto.Cipher import AES
ROOT=Path(__file__).resolve().parents[2]
src=(ROOT/"script/offline_audit/elf_3401e040.bin").read_bytes()
w=[x&0xffffffff for x in [-1230090044,2127323314,-1059689052,1415825335,-2074817314,253067825,763488977,855944017]]
key=struct.pack(">4I",*(w[i]^w[i+4] for i in range(4)))
iv=int.from_bytes(struct.pack(">4I",w[4],w[5],0,0),"big")
for cut in [0,0x40,0x100,0x200,0x400,0x800,0x1000,0x2000,0x3000,0x4000,0x5000]:
    if cut>len(src): continue
    ctr=iv+cut//16
    tail=AES.new(key,AES.MODE_CTR,nonce=b"",initial_value=ctr).decrypt(src[cut:])
    out=src[:cut]+tail
    h=hashlib.sha256(out).hexdigest()
    print(hex(cut),h,out[0x1000:0x1010].hex(),out[0x1350:0x1368].hex())
    if h=="9ec3d41b5db1baee571dbe1bebff4774b85d61e046edce96a86dd489644ce2e7":
        (ROOT/"script/offline_audit/sys_audit_collector.recovered").write_bytes(out)
        print("MATCH",hex(cut))
