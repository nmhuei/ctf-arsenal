#!/usr/bin/env python3
"""
SEKAI CTF 2026 Skyblock Solver (Paper 26.1.2)
Waits for AntiBot, connects, finds chat_command PID.
"""
import socket, struct, time, uuid, zlib, sys, json

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

class Client:
    def __init__(self, name=None, pwd=None):
        self.cp = -1
        self.uid = uuid.uuid4()
        ts = int(time.time())
        self.name = name or f"P{ts%10000}"
        self.pwd = pwd or f"pw{ts%10000}"
        self.sock = None
        self.msgs = set()
        self.loaded = False

    def send(self, pid, data=b''):
        r = wvar(pid) + data
        if self.cp >= 0:
            if len(r) >= self.cp:
                c = zlib.compress(r); f = wvar(len(r)) + c
            else: f = wvar(0) + r
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(r)) + r)

    def recv(self, timeout=0.5):
        self.sock.settimeout(timeout)
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        pl, _ = rvar(d)
        rt = b''
        while len(rt) < pl:
            c = self.sock.recv(pl - len(rt))
            if not c: return None, None
            rt += c
        if self.cp >= 0:
            dl, o = rvar(rt)
            if dl > 0:
                dec = zlib.decompress(rt[o:])
                p, o2 = rvar(dec); return p, dec[o2:]
            else: p, o2 = rvar(rt, o); return p, rt[o2:]
        else: p, o = rvar(rt); return p, rt[o:]

    def parse_chat(self, pl):
        if not pl: return ""
        def _scan(d, off):
            r = []
            while off < len(d):
                tt = d[off]
                if tt == 0: return "".join(r), off + 1
                off += 1
                if off + 2 > len(d): break
                nl = struct.unpack('>H', d[off:off+2])[0]
                name = d[off+2:off+2+nl].decode(errors='replace') if nl else ''
                off += 2 + nl
                if tt == 0x08:
                    if off + 2 > len(d): break
                    sl = struct.unpack('>H', d[off:off+2])[0]
                    if off + sl + 2 > len(d): break
                    val = d[off+2:off+2+sl].decode(errors='replace')
                    off += 2 + sl
                    if name in ('text',''): r.append(val)
                elif tt == 0x09:
                    if off + 5 > len(d): break
                    lt, ll = d[off], struct.unpack('>I', d[off+1:off+5])[0]; off += 5
                    for _ in range(ll):
                        if lt == 0x0a: s, off = _scan(d, off); r.append(s)
                        elif lt == 0x08:
                            if off + 2 > len(d): break
                            sl = struct.unpack('>H', d[off:off+2])[0]
                            if off + sl + 2 > len(d): break
                            r.append(d[off+2:off+2+sl].decode(errors='replace')); off += 2 + sl
                        else: break
                elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
                else: break
            return "".join(r), off
        try:
            result, _ = _scan(pl, 1)
            return result.replace('\xa7', '').strip()
        except: return ""

    def try_login(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        self.send(0x00, wvar(PV)+wstr(HOST)+struct.pack('>H',PORT)+wvar(2))
        self.send(0x00, wstr(self.name)+struct.pack('>QQ',self.uid.int>>64,self.uid.int&((1<<64)-1)))
        while True:
            p,pl=self.recv(15)
            if p == 0x00:
                l,o=rvar(pl); return ("BLOCKED", pl[o:o+l].decode())
            if p == 0x02: self.send(0x03); break
            elif p == 0x03: self.cp, _ = rvar(pl)
            elif p == 0x04: m, o = rvar(pl, 1); self.send(0x02, wvar(m)+wvar(0))
        return ("OK", "")

    def setup(self):
        status, msg = self.try_login()
        if status != "OK": return status, msg
        print("[+] Login OK", flush=True)

        self.send(0x00, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
        while True:
            p,pl=self.recv(5)
            if p == 0x03: break
            elif p == 0x04: self.send(0x04, pl)
            elif p == 0x05: self.send(0x05, pl)
            elif p == 0x0E:
                cnt,o=rvar(pl); resp=b''
                for _ in range(cnt):
                    l,o=rvar(pl,o); ns=pl[o:o+l].decode(); o+=l
                    l,o=rvar(pl,o); n=pl[o:o+l].decode(); o+=l
                    l,o=rvar(pl,o); v=pl[o:o+l].decode(); o+=l
                    resp+=wstr(ns)+wstr(n)+wstr(v)
                self.send(0x07,wvar(cnt)+resp)
            elif p == 0x12:
                nbt=b'\x0a\x00\x00'
                nbt+=b'\x08\x00\x08password'+struct.pack('>H',len(self.pwd))+self.pwd.encode()
                nbt+=b'\x08\x00\x07confirm'+struct.pack('>H',len(self.pwd))+self.pwd.encode()+b'\x00'
                self.send(0x08,wstr("authme:prejoin-register/submit")+wvar(len(b'\x01'+nbt))+b'\x01'+nbt)
            elif p == 0x13: self.send(0x09)
            elif p == 0x02:
                l,o=rvar(pl); return ("CFGKICK", pl[o:o+l].decode())
        print("[+] Config done", flush=True)
        return ("OK", "")

    def play(self, commands=None):
        self.send(0x03)
        self.sock.settimeout(0.5)
        t0 = time.time(); self.loaded = False
        cmds_sent = 0
        if commands is None:
            commands = ['help', 'balance', 'coins', 'tradebook help', 'tradebook list', 'shop']

        # Chat command IDs to try (skip known: 0x00, 0x0E, 0x1B, 0x2C)
        chat_ids = [0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B]
        chat_idx = 0

        while time.time()-t0 < 35:
            try:
                p,pl=self.recv(0.5)
                if p is None: break
            except socket.timeout: p = None
            except: break

            if p == 0x31 and not self.loaded:
                self.send(0x2C)
                self.send(0x0E, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
                self.loaded = True
                print(f"[+] Loaded {time.time()-t0:.1f}s", flush=True)
            elif p == 0x2C and len(pl) == 8:
                self.send(0x1B, pl)
            elif p == 0x20:
                l,o=rvar(pl,0); m=pl[o:o+l].decode(errors='replace')
                print(f"[KICK] {m[:100]}", flush=True); break
            elif p == 0x79:
                txt = self.parse_chat(pl)
                if txt and txt not in self.msgs:
                    self.msgs.add(txt); print(f"[C] {txt[:250]}", flush=True)
            elif p == 0x46:
                tid,_=rvar(pl); self.send(0x00,wvar(tid))
            elif p == 0x74:
                print("[!] Config", flush=True); break

            # Try chat commands
            now = time.time()
            if self.loaded and cmds_sent < len(commands) and now - t0 > 4 + cmds_sent * 2:
                cmd = commands[cmds_sent]
                # Try multiple formats
                formats = [
                    (chat_ids[chat_idx % len(chat_ids)], wstr(cmd) + struct.pack('>q',int(now*1000)) + struct.pack('>q',0) + wvar(0) + wvar(0) + b'\x00'),
                ]
                for pid, pld in formats:
                    self.send(pid, pld)
                    print(f">>> [0x{pid:02x}] /{cmd}", flush=True)
                    chat_idx += 1
                cmds_sent += 1

        self.sock.close()
        print(f"\n=== {len(self.msgs)} msgs {time.time()-t0:.1f}s ===", flush=True)
        for m in sorted(self.msgs): print(f"  {m[:200]}", flush=True)
        for m in self.msgs:
            if any(x in m.lower() for x in ['sekai','flag','tbctf','ctf{','skey']):
                print(f"\n*** FLAG: {m} ***", flush=True)
                return m

    def run(self):
        status, msg = self.setup()
        if status == "BLOCKED":
            print(f"[!] {msg[:50]}, waiting...", flush=True)
            return False
        if status != "OK":
            print(f"[!] {status}: {msg[:80]}", flush=True)
            return False
        self.play()
        return True

if __name__ == "__main__":
    while True:
        c = Client()
        result = c.run()
        if result:
            print("[+] Done!", flush=True)
            break
        print("[*] Retrying in 30s...", flush=True)
        time.sleep(30)
