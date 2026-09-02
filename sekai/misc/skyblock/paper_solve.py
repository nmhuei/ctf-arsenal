#!/usr/bin/env python3
"""
SEKAI CTF 2026 — Paper 26.1.2 Skyblock Solver

C->S packet IDs (Paper 26.1.2, empirically determined):
  player_loaded:   0x2C
  keep_alive:      0x1B
  teleport_confirm:0x00
  chat_command:    0x06 (tentative)
  tick_end:        DON'T SEND (causes DecoderException)
  client_settings: 0x0E (or 0x0D?)
"""
import socket, struct, time, uuid, zlib, re, json, threading

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
    # Quick NBT chat parser
    def _scan(data, off):
        r = []
        while off < len(data):
            if off >= len(data): break
            tt = data[off]
            if tt == 0: return "".join(r), off + 1
            off += 1
            if off + 2 > len(data): break
            nl = struct.unpack('>H', data[off:off+2])[0]
            name = data[off+2:off+2+nl].decode(errors='replace') if nl else ''
            off += 2 + nl
            if tt == 0x08:
                if off + 2 > len(data): break
                sl = struct.unpack('>H', data[off:off+2])[0]
                if off + sl + 2 > len(data): break
                val = data[off+2:off+2+sl].decode(errors='replace')
                off += 2 + sl
                if name in ('text', ''): r.append(val)
            elif tt == 0x09:
                if off + 5 > len(data): break
                lt, ll = data[off], struct.unpack('>I', data[off+1:off+5])[0]
                off += 5
                for _ in range(ll):
                    if lt == 0x0a:
                        s, off = _scan(data, off)
                        r.append(s)
                    elif lt == 0x08:
                        if off + 2 > len(data): break
                        sl = struct.unpack('>H', data[off:off+2])[0]
                        if off + sl + 2 > len(data): break
                        r.append(data[off+2:off+2+sl].decode(errors='replace'))
                        off += 2 + sl
                    else: break
            elif tt == 0x0a:
                s, off = _scan(data, off)
                r.append(s)
            else: break
        return "".join(r), off
    try:
        result, _ = _scan(pl, 1)
        return result.replace('\xa7', '').strip()
    except: return ""

class Client:
    def __init__(self, suffix=''):
        self.cp = -1; self.uid = uuid.uuid4()
        self.name = f"F{int(time.time())%10000}{suffix}"
        self.pwd = f"pw{int(time.time())%10000}"
        self.sock = None; self.msgs = set(); self.keep_running = True

    def send_raw(self, data):
        if self.cp >= 0:
            if len(data) >= self.cp:
                c = zlib.compress(data); f = wvar(len(data)) + c
            else: f = wvar(0) + data
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(data)) + data)

    def send_pkt(self, pid, data=b''): self.send_raw(wvar(pid) + data)

    def recv_pkt(self, timeout=0.5):
        self.sock.settimeout(timeout)
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        plen, _ = rvar(d)
        rest = b''
        while len(rest) < plen:
            c = self.sock.recv(plen - len(rest))
            if not c: return None, None
            rest += c
        if self.cp >= 0:
            dl, o = rvar(rest)
            if dl > 0:
                dec = zlib.decompress(rest[o:])
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def login(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30); self.sock.connect((HOST, PORT))
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.name) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))
        while True:
            pid, pl = self.recv_pkt(15)
            if pid == 0x00: return False
            if pid == 0x02: self.send_pkt(0x03); break
            elif pid == 0x03: self.cp, _ = rvar(pl)
            elif pid == 0x04: mid, o = rvar(pl, 1); self.send_pkt(0x02, wvar(mid) + wvar(0))
        return True

    def config(self):
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            pid, pl = self.recv_pkt(5)
            if pid == 0x03: break
            elif pid == 0x04: self.send_pkt(0x04, pl)
            elif pid == 0x05: self.send_pkt(0x05, pl)
            elif pid == 0x0E:
                cnt, o = rvar(pl); resp = b''
                for _ in range(cnt):
                    ns, o = rs(pl, o); n, o = rs(pl, o); v, o = rs(pl, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send_pkt(0x07, wvar(cnt) + resp)
            elif pid == 0x12:
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13: self.send_pkt(0x09)
            elif pid == 0x02: return False
        return True

    def run(self, commands=None):
        if not self.login(): return
        if not self.config(): return

        self.send_pkt(0x03); print(f"[+] PLAY as {self.name}", flush=True)
        loaded = False; t0 = time.time(); cmds_sent = []

        while self.keep_running:
            now = time.time()
            try:
                pid, pl = self.recv_pkt(0.5)
                if pid is None: break
            except socket.timeout: pid = None
            except: break

            if pid == 0x31 and not loaded:
                self.send_pkt(0x2C); loaded = True
                print(f"[+] Loaded (0x2C) at {now-t0:.1f}s", flush=True)
            elif pid == 0x2C and len(pl) == 8:
                self.send_pkt(0x1B, pl)
            elif pid == 0x20:
                txt = parse_chat(pl)
                print(f"[KICK] {txt[:300]}", flush=True)
                if 'timeout' not in txt.lower(): break
                print("[*] Reconnecting...", flush=True)
                break
            elif pid == 0x79:
                txt = parse_chat(pl)
                if txt and txt not in self.msgs:
                    self.msgs.add(txt)
                    print(f"[C] {txt[:350]}", flush=True)
            elif pid == 0x46:
                tid, _ = rvar(pl); self.send_pkt(0x00, wvar(tid))
            elif pid == 0x74:
                print(f"[!] Back to config", flush=True); break
            elif pid == 0x00:
                pass  # tick_end

            if loaded and commands and now - t0 > 3 + len(cmds_sent) * 5:
                cmd = commands[len(cmds_sent)]
                # Try simple format (just command string)
                m = wstr(cmd) + struct.pack('>q', int(now*1000))
                m += struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                self.send_pkt(0x06, m)
                cmds_sent.append(cmd)
                print(f">>> /{cmd}", flush=True)

            if now - t0 > 55: break

        self.sock.close()
        print(f"\n=== {len(self.msgs)} unique msgs ===", flush=True)
        for m in sorted(self.msgs):
            print(f"  {m[:200]}", flush=True)
        for m in self.msgs:
            if any(x in m.lower() for x in ['sekai', 'flag', 'tbctf', 'ctf{']):
                print(f"\n*** FLAG: {m} ***", flush=True)
                return m

if __name__ == "__main__":
    import sys
    c = Client(sys.argv[1] if len(sys.argv) > 1 else '')
    c.run(['coins', 'balance', 'tradebook help', 'tradebook list'])
