#!/usr/bin/env python3
"""
SEKAICTF Skyblock solver - Paper 26.1.2
Uses Paper-specific packet IDs from v10 working client.
"""
import socket, struct, time, uuid, zlib, json, threading, re, sys

HOST = "skyblock.chals.sekai.team"
PORT = 25565
PV = 775

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

def wstr(s): e = s.encode('utf-8'); return wvar(len(e)) + e
def rs(d, o=0): l, o = rvar(d, o); return d[o:o+l].decode('utf-8', errors='replace') if l else '', o

class SkySolver:
    def __init__(self, suffix=""):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        ts = int(time.time() % 100000)
        self.uname = "R" + str(ts % 10000) + suffix
        self.pwd = "pw" + str(ts)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.msgs = []
        self.running = True

    def send(self, pid, data=b''):
        raw = wvar(pid) + data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw); f = wvar(len(raw)) + c
            else: f = wvar(0) + raw
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(raw)) + raw)

    def recv(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: raise ConnectionError("Closed")
            d += b
            if not (b[0] & 0x80): break
        l, _ = rvar(d)
        rest = b''
        while len(rest) < l:
            c = self.sock.recv(l - len(rest))
            if not c: raise ConnectionError("Closed")
            rest += c
        if self.cp >= 0:
            dl, o = rvar(rest)
            if dl > 0: dec = zlib.decompress(rest[o:])
            else: dec = rest[o:]
            pid, o2 = rvar(dec); return pid, dec[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def log(self, m): print(m, flush=True)

    def extract_json(self, obj):
        if isinstance(obj, str): return obj
        if isinstance(obj, dict):
            parts = []
            if 'text' in obj: parts.append(str(obj['text']))
            if 'extra' in obj:
                for e in obj['extra']: parts.append(self.extract_json(e))
            if 'translate' in obj:
                args = obj.get('with', [])
                parts.append(str(args) if args else obj['translate'])
            return ''.join(parts)
        return str(obj)

    def run(self, commands=None):
        if commands is None:
            commands = ['help', 'balance', 'tradebook help', 'tradebook list',
                        'shop', 'leaderboard', 'baltop', 'island']

        # Connect + Handshake + Login
        self.sock.connect((HOST, PORT))
        self.send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        while True:
            pid, pl = self.recv()
            if pid == 0x02: self.send(0x03); break  # Login Success → Ack
            elif pid == 0x03: self.cp, _ = rvar(pl)  # Compression
            elif pid == 0x04: mid, o = rvar(pl, 1); self.send(0x02, wvar(mid)+wvar(0))

        # CONFIG state
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        while True:
            pid, pl = self.recv()
            if pid == 0x03: break  # finish_configuration
            elif pid == 0x04: self.send(0x04, pl)  # keep_alive
            elif pid == 0x05: self.send(0x05, pl)  # pong
            elif pid == 0x0e:
                cnt, o = rvar(pl)
                resp = b''
                for _ in range(cnt):
                    ns, o = rs(pl, o); n, o = rs(pl, o); v, o = rs(pl, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send(0x07, wvar(cnt) + resp)
            elif pid == 0x12:  # AuthMe form
                nbt = b'\x0a\x00\x00' + b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01')+len(nbt)) + b'\x01' + nbt)
                self.log(f"[+] Registered: {self.uname} / {self.pwd}")
            elif pid == 0x13: self.send(0x09)

        # Send config ack → PLAY
        self.send(0x03)
        self.log("[+] PLAY state")

        # Heartbeat
        def hb():
            while self.running:
                try: self.send(0x24, b'\x00' * 8)  # tick_end (v10 style)
                except: break
                time.sleep(0.5)
        threading.Thread(target=hb, daemon=True).start()

        # Play loop - USE v10 packet IDs
        ci = 0
        t0 = time.time()
        loaded = False
        self.sock.settimeout(10)

        while self.running:
            now = time.time()
            try: pid, pl = self.recv()
            except (socket.timeout, ConnectionError): break
            except: break

            if pid == 0x2c:  # Keep Alive (v10 style)
                self.send(0x1c, pl)
            elif pid == 0x31:  # Login/Join
                if not loaded:
                    self.send(0x2c)  # Player Loaded
                    self.send(0x0e, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
                    self.log("[+] Player loaded")
            elif pid == 0x48:  # Position
                self.send(0x00, wvar(0))
            elif pid == 0x20:  # Disconnect
                txt = pl.decode(errors='replace')
                txt = re.sub(r'\xa7.', '', txt)
                try:
                    j = json.loads(txt)
                    txt = self.extract_json(j)
                except: pass
                self.log(f"[KICK] {txt[:300]}")
                break
            elif pid == 0x79:  # System Chat
                msg, _ = rs(pl)
                if msg.startswith("{"):
                    try: j = json.loads(msg); msg = self.extract_json(j)
                    except: pass
                msg = re.sub(r'\xa7.', '', msg).strip()
                if msg:
                    self.msgs.append(msg)
                    self.log(f"[C] {msg[:500]}")
            elif pid == 0x6E:  # Title/Action bar
                pass
            elif pid == 0x55:  # action_bar
                try:
                    msg, _ = rs(pl)
                    if msg.startswith("{"): j = json.loads(msg); msg = self.extract_json(j)
                    msg = re.sub(r'\xa7.', '', msg).strip()
                    if msg: self.msgs.append(msg); self.log(f"[A] {msg[:300]}")
                except: pass
            elif pid == 0x0E:  # Open Screen
                pass

            # Send commands - use 0x07 for chat_command (v10 style)
            if ci < len(commands) and now - t0 > 3 + ci * 5:
                cmd = commands[ci]
                self.log(f">>> /{cmd}")
                self.send(0x07, wstr(cmd))  # chat_command_signed (Paper)
                ci += 1

            if ci >= len(commands) and now - t0 > 45:
                break

        self.running = False
        self.sock.close()

        self.log(f"\n{'='*60}")
        self.log(f"Results ({len(self.msgs)} messages):")
        self.log('='*60)
        for m in self.msgs:
            self.log(f"  {m}")

        # Check for flag
        for m in self.msgs:
            if any(x in m.lower() for x in ['sekai', 'flag', 'tbctf', '{']):
                self.log(f"\n*** FLAG: {m} ***")

        return self.msgs


if __name__ == "__main__":
    suffix = sys.argv[1] if len(sys.argv) > 1 else ''
    s = SkySolver(suffix)
    s.run()
