from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
INITIAL=(0x670e8462,0x306591b4,0x8372919d)
tab=[]
for i in range(256):
    c=i
    for _ in range(8):
        c=(c>>1) ^ (0xedb88320 if c&1 else 0)
    tab.append(c & 0xffffffff)

def decrypt(data):
    a,b,c=INITIAL
    out=bytearray()
    for e in data:
        t=(c&0xffff)|2
        p=e ^ (((t*(t^1))>>8)&255)
        out.append(p)
        a=((a>>8)^tab[(a^p)&255]) & 0xffffffff
        b=((b+(a&255))*134775813+1) & 0xffffffff
        c=((c>>8)^tab[(c^(b>>24))&255]) & 0xffffffff
    return bytes(out)

arc=(HERE/"documents_reassembled.zip").read_bytes()
pos=0x1ee2
h=struct.unpack_from("<4s5H3I2H",arc,pos)
name_len,extra_len=h[9],h[10]
begin=pos+30+name_len+extra_len
claimed=h[7]
avail=max(0,min(claimed,len(arc)-begin))
print("archive_len",hex(len(arc)),"data_begin",hex(begin),"claimed",claimed,"available",avail)
raw=arc[begin:begin+avail]
plain=decrypt(raw)
print("enc_header",plain[:12].hex())
payload=plain[12:]
print("payload_len",len(payload))
print(payload.decode("utf-8","replace"))
(HERE/"staged_encryption_token.partial.txt").write_bytes(payload)
