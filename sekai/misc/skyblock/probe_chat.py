#!/usr/bin/env python3
"""Probe Paper 26.1.2 C->S chat_command ID by trying each"""
import socket, struct, time, uuid, zlib

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

def rs(d, o=0):
    l, o = rvar(d, o)
    return d[o:o+l].decode(), o+l

def parse_chat(pl):
    if not pl: return ""
    def _scan(d, o):
        r = []
        while o < len(d):
            tt = d[o]
            if tt == 0: return "".join(r), o+1
            o += 1
            if o+2 > len(d): break
            nl = struct.unpack('>H', d[o:o+2])[0]
            name = d[o+2:o+2+nl].decode(errors='replace') if nl else ''
            o += 2 + nl
            if tt == 0x08:
                if o+2 > len(d): break
                sl = struct.unpack('>H', d[o:o+2])[0]
                if o+sl+2 > len(d): break
                val = d[o+2:o+2+sl].decode(errors='replace')
                o += 2+sl
                if name in ('text',''): r.append(val)
            elif tt == 0x09:
                if o+5 > len(d): break
                lt, ll = d[o], struct.unpack('>I', d[o+1:o+5])[0]; o += 5
                for _ in range(ll):
                    if lt == 0x0a: s, o = _scan(d, o); r.append(s)
                    elif lt == 0x08:
                        if o+2 > len(d): break
                        sl = struct.unpack('>H', d[o:o+2])[0]
                        if o+sl+2 > len(d): break
                        r.append(d[o+2:o+2+sl].decode(errors='replace')); o += 2+sl
                    else: break
            elif tt == 0x0a: s, o = _scan(d, o); r.append(s)
            else: break
        return "".join(r), o
    r, _ = _scan(pl, 1)
    return r.replace('\xa7', '').strip()

class Bot:
    def __init__(self):
        self.cp = -1; self.uid = uuid.uuid4()
        self.name = "G" + str(int(time.time())%10000)
        self.pwd = "pw" + str(int(time.time())%10000)

    def send(self, pid, data=b''):
        raw = wvar(pid) + data
        if self.cp >= 0:
            c = zlib.compress(raw) if len(raw) >= self.cp else b''
            f = wvar(len(raw))+c if len(raw) >= self.cp else wvar(0)+raw
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(raw)) + raw)

    def recv(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None,None
            d += b
            if not (b[0]&0x80): break
        pl,_=rvar(d)
        rt=b''
        while len(rt)<pl:
            c=self.sock.recv(pl-len(rt))
            if not c: return None,None
            rt+=c
        if self.cp>=0:
            dl,o=rvar(rt)
            if dl>0:
                dec=zlib.decompress(rt[o:]);pid,o2=rvar(dec);return pid,dec[o2:]
            else: pid,o2=rvar(rt,o);return pid,rt[o2:]
        else: pid,o=rvar(rt);return pid,rt[o:]

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30); self.sock.connect((HOST, PORT))
        self.send(0x00, wvar(PV)+wstr(HOST)+struct.pack('>H',PORT)+wvar(2))
        self.send(0x00, wstr(self.name)+struct.pack('>QQ',self.uid.int>>64,self.uid.int&((1<<64)-1)))
        while True:
            p,pl=self.recv()
            if p==0x00: return False
            if p==0x02: self.send(0x03); break
            elif p==0x03: self.cp,_=rvar(pl)
            elif p==0x04: m,o=rvar(pl,1); self.send(0x02, wvar(m)+wvar(0))
        return True

    def config(self):
        self.send(0x00, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
        while True:
            p,pl=self.recv()
            if p==0x03: break
            elif p==0x04: self.send(0x04, pl)
            elif p==0x05: self.send(0x05, pl)
            elif p==0x0E:
                cnt,o=rvar(pl); resp=b''
                for _ in range(cnt):
                    ns,o=rs(pl,o); n,o=rs(pl,o); v,o=rs(pl,o)
                    resp+=wstr(ns)+wstr(n)+wstr(v)
                self.send(0x07, wvar(cnt)+resp)
            elif p==0x12:
                nbt=b'\x0a\x00\x00'
                nbt+=b'\x08\x00\x08password'+struct.pack('>H',len(self.pwd))+self.pwd.encode()
                nbt+=b'\x08\x00\x07confirm'+struct.pack('>H',len(self.pwd))+self.pwd.encode()+b'\x00'
                self.send(0x08, wstr("authme:prejoin-register/submit")+wvar(len(b'\x01'+nbt))+b'\x01'+nbt)
            elif p==0x13: self.send(0x09)
            elif p==0x02: return False
        return True

    def try_cmd(self, pid, cmd, now):
        """Send chat command at given packet ID, return True if no immediate disconnect"""
        # Try 3 formats: simple string, signed, and unsigned-with-signature
        formats = [
            (0, wstr(cmd) + struct.pack('>q',int(now*1000)) + struct.pack('>q',0) + wvar(0) + wvar(0) + b'\x00'),
            (1, wstr(cmd)),
            (2, wstr(cmd) + struct.pack('>q',int(now*1000)) + struct.pack('>q',0) + wvar(1) + wvar(1) + b'\x01'),
        ]
        for fmt_id, payload in formats:
            self.send(pid, payload)

    def run(self):
        if not self.connect(): return
        if not self.config(): return
        self.send(0x03)
        self.sock.settimeout(0.5)
        t0 = time.time()
        loaded = False
        tested_ids = []
        cmd_test_idx = 0
        chat_pids = [0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e,
                     0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
                     0x18, 0x19, 0x1a, 0x1c, 0x1d, 0x1e, 0x1f, 0x20,
                     0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a]  # skip 0x1B (KA), 0x21 (player_loaded?)
        alive = True

        while alive and time.time()-t0 < 40:
            now = time.time()
            try:
                pid, pl = self.recv()
                if pid is None: break
            except socket.timeout: pid = None
            except: break

            if pid == 0x31 and not loaded:
                self.send(0x2C); loaded = True
                print(f"[+] Loaded {now-t0:.1f}s", flush=True)
            elif pid == 0x2C and len(pl) == 8:
                self.send(0x1B, pl)
            elif pid == 0x20:
                txt = parse_chat(pl)
                print(f"[KICK] {txt[:200]}", flush=True)
                alive = False
            elif pid == 0x79:
                txt = parse_chat(pl)
                if txt: print(f"[C] {txt[:120]}", flush=True)
            elif pid == 0x46:
                tid, _ = rvar(pl); self.send(0x00, wvar(tid))

            # Test commands one at a time
            if loaded and cmd_test_idx < len(chat_pids) and now - t0 > 5 + cmd_test_idx * 0.5:
                pid_test = chat_pids[cmd_test_idx]
                print(f"\n--- Trying cmd ID 0x{pid_test:02x} ---", flush=True)
                self.try_cmd(pid_test, "coins", now)
                tested_ids.append(pid_test)
                cmd_test_idx += 1
                time.sleep(0.3)

        self.sock.close()
        print(f"\nTested IDs: {[f'0x{p:02x}' for p in tested_ids]}", flush=True)

Bot().run()
