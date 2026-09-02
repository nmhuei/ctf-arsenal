#!/usr/bin/env python3
"""
Paper 26.1.2 Skyblock CTF Solver — final version
Connects, registers, stays alive 20+ seconds, captures all server data.
"""
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

class Bot:
    def __init__(self):
        self.cp = -1
        self.uid = uuid.uuid4()
        ts = int(time.time())
        self.name = f"B{ts%10000}"
        self.pwd = f"pw{ts%10000}"
        self.sock = None
        self.msgs = []

    def send(self, pid, data=b''):
        r = wvar(pid) + data
        if self.cp >= 0:
            if len(r) >= self.cp:
                c = zlib.compress(r); f = wvar(len(r)) + c
            else: f = wvar(0) + r
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(r)) + r)

    def recv(self):
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

    def setup(self):
        """Login + config + AuthMe registration"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        # Handshake + Login
        self.send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send(0x00, wstr(self.name) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))
        while True:
            p, pl = self.recv()
            if p == 0x00: return False, "ANTIBOT"
            if p == 0x02: self.send(0x03); break
            elif p == 0x03: self.cp, _ = rvar(pl)
            elif p == 0x04:
                m, o = rvar(pl, 1); self.send(0x02, wvar(m) + wvar(0))

        # Client settings in config
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            p, pl = self.recv()
            if p == 0x03: break  # Finish configuration
            elif p == 0x04: self.send(0x04, pl)
            elif p == 0x05: self.send(0x05, pl)
            elif p == 0x0E:
                cnt, o = rvar(pl); resp = b''
                for _ in range(cnt):
                    l, o = rvar(pl, o); ns = pl[o:o+l].decode(); o += l
                    l, o = rvar(pl, o); n = pl[o:o+l].decode(); o += l
                    l, o = rvar(pl, o); v = pl[o:o+l].decode(); o += l
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send(0x07, wvar(cnt) + resp)
            elif p == 0x12:
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01' + nbt)) + b'\x01' + nbt)
            elif p == 0x13: self.send(0x09)
            elif p == 0x02: return False, "CFGKICK"

        # Enter PLAY
        self.send(0x03)
        return True, "OK"

    def parse_chat(self, pl):
        """Extract text from NBT chat component"""
        if not pl: return ""
        def _scan(d, off):
            r = []
            while off < len(d):
                tt = d[off]
                if tt == 0: return "".join(r), off + 1
                off += 1
                if off + 2 > len(d): break
                nl = struct.unpack('>H', d[off:off+2])[0]
                nm = d[off+2:off+2+nl].decode(errors='replace') if nl else ''
                off += 2 + nl
                if tt == 0x08:
                    if off + 2 > len(d): break
                    sl = struct.unpack('>H', d[off:off+2])[0]
                    if off + sl + 2 > len(d): break
                    val = d[off+2:off+2+sl].decode(errors='replace'); off += 2 + sl
                    if nm in ('text', ''): r.append(val)
                elif tt == 0x09:
                    if off + 5 > len(d): break
                    lt, ll = d[off], struct.unpack('>I', d[off+1:off+5])[0]; off += 5
                    for _ in range(ll):
                        if lt == 0x0a: s, off = _scan(d, off); r.append(s)
                        elif lt == 0x08:
                            if off + 2 > len(d): break
                            sl = struct.unpack('>H', d[off:off+2])[0]
                            r.append(d[off+2:off+2+sl].decode(errors='replace')); off += 2 + sl
                        else: break
                elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
                else: break
            return "".join(r), off
        try:
            result, _ = _scan(pl, 1)
            return result.replace('\xa7', '').strip()
        except: return ""

    def listen(self, timeout=30):
        """
        Listen, capture chat, try early cmd.
        """
        self.sock.settimeout(0.5)
        t0 = time.time()
        loaded = False
        all_packets = {}
        cmd_sent = False

        while time.time() - t0 < timeout:
            try:
                p, pl = self.recv()
                if p is None: break
            except socket.timeout:
                # Send 1 cmd early
                if loaded and not cmd_sent and time.time()-t0 > 3:
                    self.send(0x06, wstr("coins"))
                    print(f"[CMD] /skyblock @{time.time()-t0:.1f}s", flush=True)
                    cmd_sent = True
                continue
            except: break

            now = time.time() - t0

            if p == 0x31 and not loaded:
                self.send(0x2C)  # Player loaded
                self.send(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                loaded = True
                print(f"[+] PLAY ready @{now:.1f}s", flush=True)

            elif p == 0x79:
                txt = self.parse_chat(pl)
                if txt and txt not in self.msgs:
                    self.msgs.append(txt)
                    # Don't show welcome spam
                    if 'Welcome' not in txt and 'Build your' not in txt and 'Harvest' not in txt:
                        print(f"[CHAT] {txt[:200]}", flush=True)

            elif p == 0x20:
                l, o = rvar(pl, 0); m = pl[o:o+l].decode(errors='replace')
                print(f"[KICK] @{now:.1f}s: {m[:60]}", flush=True)
                return False

            elif p == 0x46 and len(pl) < 50:
                tid, _ = rvar(pl)
                self.send(0x00, wvar(tid))  # Teleport confirm

        print(f"\n[+] {len(self.msgs)} messages, {len(all_packets)} unique packet types", flush=True)
        return True

    def close(self):
        try: self.sock.close()
        except: pass


if __name__ == "__main__":
    for attempt in range(50):
        b = Bot()
        ok, status = b.setup()
        if not ok:
            print(f"[{attempt}] {status}", flush=True)
            b.close()
            if status == "ANTIBOT":
                time.sleep(60)
            else:
                time.sleep(5)
            continue

        print(f"[{attempt}] Connected as {b.name}", flush=True)
        b.listen(25)
        b.close()

        # Check for flag
        all_text = " ".join(b.msgs)
        for keyword in ['sekai', 'flag{', 'sKey', 'tbctf', 'ctf{', 'SEKAI']:
            if keyword in all_text:
                print(f"\n*** FLAG FOUND: {all_text} ***", flush=True)
                sys.exit(0)

        print("[*] No flag in this session, retrying in 10s...", flush=True)
        time.sleep(10)
