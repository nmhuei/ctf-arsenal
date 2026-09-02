#!/usr/bin/env python3
"""Probe Paper 26.1.2 C->S chat_command ID"""
import socket, struct, time, uuid, zlib, sys

HOST, PORT, PV = "skyblock.chals.sekai.team", 25565, 775

def wvar(v):
    out = bytearray()
    while True:
        if v & 0xFFFFFF80 == 0: out.append(v & 0x7F); return bytes(out)
        out.append((v & 0x7F) | 0x80); v = (v >> 7) & 0xFFFFFFFF

def rvar(d, o=0):
    r, s = 0, 0
    while True:
        b = d[o]; r |= (b & 0x7F) << s; s += 7; o += 1
        if not (b & 0x80): return r, o

def wstr(s): e = s.encode(); return wvar(len(e)) + e

def try_pid(pid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    try:
        sock.connect((HOST, PORT))
        cp = -1
        uid = uuid.uuid4()
        name = f"H{int(time.time())%10000:x}{pid}"
        pwd = f"pw{int(time.time())%10000}"

        def send(p, data=b''):
            raw = wvar(p) + data
            nonlocal cp
            if cp >= 0:
                if len(raw) >= cp: c = zlib.compress(raw); f = wvar(len(raw)) + c
                else: f = wvar(0) + raw
                sock.sendall(wvar(len(f)) + f)
            else: sock.sendall(wvar(len(raw)) + raw)

        def recv():
            nonlocal cp
            d = b''
            while True:
                b = sock.recv(1)
                if not b: return None, None
                d += b
                if not (b[0] & 0x80): break
            pl, _ = rvar(d)
            rt = b''
            while len(rt) < pl:
                c = sock.recv(pl - len(rt))
                if not c: return None, None
                rt += c
            if cp >= 0:
                dl, o = rvar(rt)
                if dl > 0: dec = zlib.decompress(rt[o:]); p, o2 = rvar(dec); return p, dec[o2:]
                else: p, o2 = rvar(rt, o); return p, rt[o2:]
            else: p, o = rvar(rt); return p, rt[o:]
        cp_ref = [cp]
        def send2(p, data=b''):
            nonlocal cp
            send(p, data)
        def recv2():
            return recv()

        # Login
        send(0x00, wvar(PV)+wstr(HOST)+struct.pack('>H',PORT)+wvar(2))
        send(0x00, wstr(name)+struct.pack('>QQ',uid.int>>64,uid.int&((1<<64)-1)))
        while True:
            p,pl=recv()
            if p==0x00: return "login_reject"
            if p==0x02: send(0x03); break
            elif p==0x03: cp,_=rvar(pl)
            elif p==0x04: m,o=rvar(pl,1); send(0x02,wvar(m)+wvar(0))

        # Config
        send(0x00, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
        while True:
            p,pl=recv()
            if p==0x03: break
            elif p==0x04: send(0x04,pl)
            elif p==0x05: send(0x05,pl)
            elif p==0x0E:
                cnt,o=rvar(pl); resp=b''
                for _ in range(cnt):
                    l,o=rvar(pl,o); ns=pl[o:o+l].decode(); o+=l
                    l,o=rvar(pl,o); n=pl[o:o+l].decode(); o+=l
                    l,o=rvar(pl,o); v=pl[o:o+l].decode(); o+=l
                    resp+=wstr(ns)+wstr(n)+wstr(v)
                send(0x07,wvar(cnt)+resp)
            elif p==0x12:
                nbt=b'\x0a\x00\x00'
                nbt+=b'\x08\x00\x08password'+struct.pack('>H',len(pwd))+pwd.encode()
                nbt+=b'\x08\x00\x07confirm'+struct.pack('>H',len(pwd))+pwd.encode()+b'\x00'
                send(0x08,wstr("authme:prejoin-register/submit")+wvar(len(b'\x01'+nbt))+b'\x01'+nbt)
            elif p==0x13: send(0x09)
            elif p==0x02: return "config_kick"

        # PLAY
        send(0x03)
        sock.settimeout(0.5)
        t0=time.time(); loaded=False

        while time.time()-t0 < 12:
            try:
                p,pl=recv()
                if p is None: return "disconnect"
            except socket.timeout: p=None
            except: return "error"

            if p==0x31 and not loaded:
                send(0x2C); loaded=True
            elif p==0x2C and len(pl)==8:
                send(0x1B,pl)
            elif p==0x20:
                l,o=rvar(pl,0); m=pl[o:o+l].decode(errors='replace')
                return f"KICK:{m[:120]}"
            elif p==0x46:
                tid,_=rvar(pl); send(0x00,wvar(tid))

            if loaded and time.time()-t0 > 3:
                pld = wstr("coins") + struct.pack('>q',int(time.time()*1000))
                pld += struct.pack('>q',0)+wvar(0)+wvar(0)+b'\x00'
                send(pid, pld)
                # Wait for response
                time.sleep(0.5)
                try:
                    p2,pl2=recv()
                    if p2==0x20:
                        l,o=rvar(pl2,0); m=pl2[o:o+l].decode(errors='replace')
                        return f"KICK:{m[:120]}"
                    elif p2==0x79:
                        l,o=rvar(pl2,0); m=pl2[o:o+l].decode(errors='replace')
                        return f"OK: {m[:120]}"
                except: pass
                return "sent_quietly"

        return f"timeout"
    except Exception as e:
        return f"EX:{type(e).__name__}:{e}"
    finally:
        sock.close()

if __name__ == "__main__":
    pids = [0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1a]
    for pid in pids:
        r = try_pid(pid)
        print(f"0x{pid:02x}: {r}", flush=True)
