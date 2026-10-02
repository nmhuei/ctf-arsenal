from pathlib import Path
import struct
from Crypto.Cipher import AES

HERE=Path(__file__).resolve().parent
plain=(HERE/"collector_pagecache_exact.bin").read_bytes()[:4096]
w=[x&0xffffffff for x in [-1230090044,2127323314,-1059689052,1415825335,-2074817314,253067825,763488977,855944017]]
key=struct.pack(">4I",*(w[i]^w[i+4] for i in range(4)))
iv=int.from_bytes(struct.pack(">4I",w[4],w[5],0,0),"big")
ct=AES.new(key,AES.MODE_CTR,nonce=b"",initial_value=iv).encrypt(plain)
lines=["rule collector_cipher_fragments {","  strings:"]
for off in range(0,4096,16):
    b=ct[off:off+16]
    if len(b)==16:
        lines.append(f'    $b_{off:04x} = {{ {b.hex(" ")} }}')
lines += ["  condition: any of them","}"]
(HERE/"collector_cipher_fragments.yar").write_text("\n".join(lines)+"\n")
print("patterns",len(range(0,4096,16)))
