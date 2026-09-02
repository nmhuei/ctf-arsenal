#!/usr/bin/env python3
"""
Skyblock one-shot — clean full flow, no probing, just listen.
Login → AuthMe register → PLAY state → capture all data silently.
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

class OneShot:
    def __init__(self):
        self.cp = -1
        self.uid = uuid.uuid4()
        ts = int(time.time())
        self.name = f"Pl{ts%10000}"
        self.pwd = f"pl{ts%10000}"
        self.sock = None
        self.msgs = []
        self.interesting = []

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

    def run(self):
        print(f"\n[*] Connecting as {self.name}...", flush=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        # === LOGIN + HANDSHAKE ===
        self.send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send(0x00, wstr(self.name) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        while True:
            p, pl = self.recv()
            if p is None: return print("[!] Disconnected during login")
            if p == 0x00:
                l, o = rvar(pl); msg = pl[o:o+l].decode(errors='replace')
                return print(f"[!] AntiBot: {msg[:60]}")
            if p == 0x02:
                self.send(0x03); print("[+] Login OK → PLAY", flush=True); break
            elif p == 0x03:
                self.cp, _ = rvar(pl)
                print(f"[+] Compression={self.cp}", flush=True)
                # Need login ack too
            elif p == 0x04:
                m, o = rvar(pl, 1); self.send(0x02, wvar(m) + wvar(0))

        # === CONFIG STATE ===
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            p, pl = self.recv()
            if p is None: return print("[!] Disconnected during config")
            if p == 0x03:
                print("[+] Config done", flush=True); break
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
                print("[+] AuthMe registration sent", flush=True)
            elif p == 0x13: self.send(0x09)
            elif p == 0x02:
                l, o = rvar(pl); return print(f"[!] Config kick: {pl[o:o+l].decode(errors='replace')[:60]}")

        # === PLAY STATE (NO C→S except init) ===
        self.send(0x03)
        self.sock.settimeout(0.5)
        t0 = time.time()
        loaded = False
        ka_count = 0
        packet_counts = {}

        print("[*] Listening (sending nothing but init)...", flush=True)

        while time.time() - t0 < 30:
            try:
                p, pl = self.recv()
                if p is None: break
            except socket.timeout: continue
            except: break

            dt = time.time() - t0
            packet_counts[p] = packet_counts.get(p, 0) + 1

            if p == 0x31 and not loaded:
                self.send(0x2C)   # player_loaded
                self.send(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                loaded = True
                print(f"[+] PLAY init @{dt:.1f}s", flush=True)

            elif p == 0x79:
                txt = self.parse_chat(pl)
                if txt and txt not in self.msgs:
                    self.msgs.append(txt)
                    print(f"[C] {txt[:180]}", flush=True)

            elif p == 0x2C and len(pl) == 8:
                ka_count += 1  # ignore keep_alive

            elif p == 0x20:
                l, o = rvar(pl, 0); m = pl[o:o+l].decode(errors='replace')
                print(f"[!] KICK @{dt:.1f}s: {m[:60]}", flush=True)
                return

            elif p == 0x46 and len(pl) < 50:
                tid, _ = rvar(pl); self.send(0x00, wvar(tid))

            # Track interesting packets
            if len(pl) > 100 and p not in (0x2d, 0x10, 0x3d, 0x2c):
                content = repr(pl[:80])
                if p not in [x[0] for x in self.interesting]:
                    self.interesting.append((p, len(pl), dt))
                    if p in (0x63, 0x66, 0x65, 0x56, 0x62, 0x6e):
                        print(f"[PKT] 0x{p:02x} len={len(pl)} @{dt:.1f}s", flush=True)

        dur = time.time() - t0
        print(f"\n{'='*50}", flush=True)
        print(f"[+] Session: {dur:.1f}s", flush=True)
        print(f"[+] Packets: {sum(packet_counts.values())} total, {len(packet_counts)} types", flush=True)
        print(f"[+] KeepAlives: {ka_count}", flush=True)
        print(f"[+] Chat messages: {len(self.msgs)}", flush=True)

        # Show unique packet types
        print(f"\n[*] Packet summary:", flush=True)
        for pid, count in sorted(packet_counts.items()):
            if count > 0:
                print(f"  0x{pid:02x}: {count}x", flush=True)

        # Show all chat messages
        print(f"\n[*] Messages:", flush=True)
        for m in self.msgs:
            print(f"  {m[:200]}", flush=True)

        # Extract flag
        all_text = " ".join(self.msgs)
        for kw in ['sekai', 'flag{', 'sKey', 'tbctf', 'ctf{', 'SEKAI']:
            if kw in all_text.lower():
                print(f"\n*** FLAG: {all_text} ***", flush=True)

        self.sock.close()

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


if __name__ == "__main__":
    bot = OneShot()
    bot.run()
