#!/usr/bin/env python3
"""Debug Paper kick reason"""
import socket, struct, time, uuid, zlib

HOST,PORT,PV="skyblock.chals.sekai.team",25565,775
wvar=lambda v:(lambda out=bytearray():[out.append(v&0x7F)if v&0xFFFFFF80==0 else(out.append((v&0x7F)|0x80),setattr(lambda:0,'x',exec('v=(v>>7)&0xFFFFFFFF'))or 0)for _ in iter(lambda:v&0xFFFFFF80!=0,[])]and bytes(out))()

def wvar(v):
    out=bytearray()
    while True:
        if v&0xFFFFFF80==0:out.append(v&0x7F);return bytes(out)
        out.append((v&0x7F)|0x80);v=(v>>7)&0xFFFFFFFF

def rvar(d,o=0):
    r,s=0,0
    while True:
        b=d[o];r|=(b&0x7F)<<s;s+=7;o+=1
        if not(b&0x80):return r,o

def wstr(s):e=s.encode();return wvar(len(e))+e

sock=socket.socket();sock.settimeout(20);sock.connect((HOST,PORT))
cp=-1;uid=uuid.uuid4();name="K"+str(int(time.time())%10000)
pwd="pw"+str(int(time.time())%10000)

def send(pid,data=b''):
    global cp
    r=wvar(pid)+data
    if cp>=0:
        c=zlib.compress(r)if len(r)>=cp else b''
        f=wvar(len(r))+c if len(r)>=cp else wvar(0)+r
        sock.sendall(wvar(len(f))+f)
    else:sock.sendall(wvar(len(r))+r)

def recv():
    global cp
    d=b''
    while True:
        b=sock.recv(1)
        if not b:return None,None
        d+=b
        if not(b[0]&0x80):break
    pl,_=rvar(d);rt=b''
    while len(rt)<pl:c=sock.recv(pl-len(rt));rt+=c
    if cp>=0:
        dl,o=rvar(rt)
        if dl>0:dec=zlib.decompress(rt[o:]);p,o2=rvar(dec);return p,dec[o2:]
        else:p,o2=rvar(rt,o);return p,rt[o2:]
    else:p,o=rvar(rt);return p,rt[o:]

send(0x00,wvar(PV)+wstr(HOST)+struct.pack('>H',PORT)+wvar(2))
send(0x00,wstr(name)+struct.pack('>QQ',uid.int>>64,uid.int&((1<<64)-1)))
while True:
    p,pl=recv()
    if p==0x00:l,o=rvar(pl);print(f"BLOCKED:{pl[o:o+l].decode()[:40]}");exit()
    if p==0x02:send(0x03);break
    elif p==0x03:cp,_=rvar(pl)
    elif p==0x04:m,o=rvar(pl,1);send(0x02,wvar(m)+wvar(0))
print("+Login")

send(0x00,wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
while True:
    p,pl=recv()
    if p==0x03:break
    elif p==0x04:send(0x04,pl)
    elif p==0x05:send(0x05,pl)
    elif p==0x0E:
        cnt,o=rvar(pl);resp=b''
        for _ in range(cnt):
            l,o=rvar(pl,o);ns=pl[o:o+l].decode();o+=l
            l,o=rvar(pl,o);n=pl[o:o+l].decode();o+=l
            l,o=rvar(pl,o);v=pl[o:o+l].decode();o+=l
            resp+=wstr(ns)+wstr(n)+wstr(v)
        send(0x07,wvar(cnt)+resp)
    elif p==0x12:
        nbt=b'\x0a\x00\x00';nbt+=b'\x08\x00\x08password'+struct.pack('>H',len(pwd))+pwd.encode()
        nbt+=b'\x08\x00\x07confirm'+struct.pack('>H',len(pwd))+pwd.encode()+b'\x00'
        send(0x08,wstr("authme:prejoin-register/submit")+wvar(len(b'\x01'+nbt))+b'\x01'+nbt)
    elif p==0x13:send(0x09)
    elif p==0x02:l,o=rvar(pl);print(f"CFG:{pl[o:o+l].decode()[:40]}");exit()
print("+Config")

send(0x03);sock.settimeout(0.5)
t0=time.time();loaded=False

while time.time()-t0<15:
    try:
        pid,pl=recv()
        if pid is None:break
    except socket.timeout:pid=None
    except:break

    if pid==0x31 and not loaded:
        send(0x2C);send(0x0E,wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
        loaded=True;print(f"+Loaded {time.time()-t0:.2f}s")
    elif pid==0x2C and len(pl)==8:send(0x1B,pl)
    elif pid==0x3d and len(pl)==4:
        # Try responding to ping
        send(0x22,pl)
    elif pid==0x20:
        print(f"\n=== KICK @{time.time()-t0:.2f}s ===",flush=True)
        print(f"len={len(pl)} hex={pl.hex()}",flush=True)
        print(f"ascii={pl!r}",flush=True)
        # Try parse as various things
        for off in range(min(len(pl),20)):
            try:l,o=rvar(pl,off);t=pl[o:o+l].decode(errors='replace');print(f"str@{off}:{t[:120]}",flush=True)
            except:pass
        break
    elif pid==0x79:pass
    elif pid==0x46:tid,_=rvar(pl);send(0x00,wvar(tid))
    elif pid is not None and pid not in (0x2d,0x00,0x01,0x63,0x83,0x3d,0x65,0x36,0x2f,0x35,0x38,0x71,0x23,0x66,0x7a,0x8a,0x76,0x0a,0x12,0x14,0x40,0x4a,0x48,0x69,0x85,0x22,0x18,0x56,0x61,0x26,0x7f,0x80,0x62,0x6a,0x6e,0x5f,0x5e,0x6f,0x4f,0x59,0x58,0x5b,0x5c,0x82,0x67,0x68,0x8c,0x4c,0x6b):
        print(f"??? 0x{pid:02x} len={len(pl)} h={pl[:40].hex()}",flush=True)

sock.close();print(f"Done {time.time()-t0:.1f}s")
PYEOF
