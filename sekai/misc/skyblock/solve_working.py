"""
SEKAI CTF 2026 — Skyblock Solver
Minecraft 26.1.2 (Protocol 775)

Connects, explores tradebook economy, finds flag.
Uses EXACT same packet format as working v10 client.
"""
import socket, struct, time, uuid, zlib, re

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

# ─── NBT Parser ────────────────────────────────────
def parse_nbt(data, o=0, anon=False, depth=0):
    if depth > 30 or o >= len(data): return None, o
    tt = data[o]; o += 1
    if tt == 0: return None, o
    name = ''
    if not anon:
        if o + 2 > len(data): return None, o
        nl = struct.unpack('>H', data[o:o+2])[0]; o += 2
        if nl: name = data[o:o+nl].decode(errors='replace'); o += nl
    if tt == 0x08:
        if o + 2 > len(data): return None, o
        vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
        v = data[o:o+vl].decode(errors='replace'); o += vl
        return {'t': 's', 'n': name, 'v': v}, o
    elif tt == 0x0a:
        fields = {}
        while o < len(data) and data[o] != 0:
            r, o = parse_nbt(data, o, False, depth+1)
            if r and r['n']: fields[r['n']] = r
        if o < len(data) and data[o] == 0: o += 1
        return {'t': 'c', 'n': name, 'v': fields}, o
    elif tt == 0x09:
        lt, ll = data[o], struct.unpack('>I', data[o+1:o+5])[0]; o += 5
        items = []
        for _ in range(ll):
            if lt == 0x08:
                vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                items.append({'t': 's', 'n': '', 'v': data[o:o+vl].decode(errors='replace')}); o += vl
            elif lt == 0x0a:
                fields = {}
                while o < len(data) and data[o] != 0:
                    r, o = parse_nbt(data, o, False, depth+1)
                    if r and r['n']: fields[r['n']] = r
                if o < len(data) and data[o] == 0: o += 1
                items.append({'t': 'c', 'n': '', 'v': fields})
            elif lt == 0x01: items.append({'t': 'b', 'n': '', 'v': data[o]}); o += 1
            else: break
        return {'t': 'l', 'n': name, 'v': items}, o
    return None, o

def chat_text(node):
    if node is None: return ''
    if node['t'] == 's':
        if node['n'] in ('text', 'translate', ''): return node['v']
        return ''
    elif node['t'] == 'c':
        parts = []
        for fval in node['v'].values():
            t = chat_text(fval)
            if t: parts.append(t)
        return ''.join(parts)
    elif node['t'] == 'l':
        return ''.join(chat_text(i) for i in node['v'])
    return ''


# ─── Client ────────────────────────────────────────
class Solver:
    def __init__(self, suffix):
        ts = int(time.time() % 10000)
        self.uname = f"B{ts}"
        self.pwd = f"pw{ts}"
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []
        self.loaded = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        print(f"[*] {self.uname} connecting...", flush=True)

    def send_raw(self, data):
        raw = data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw); f = wvar(len(raw)) + c
            else: f = wvar(0) + raw
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(raw)) + raw)

    def send_pkt(self, pid, data=b''):
        self.send_raw(wvar(pid) + data)

    def recv(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        l, _ = rvar(d)
        rest = b''
        while len(rest) < l:
            c = self.sock.recv(l - len(rest))
            if not c: return None, None
            rest += c
        if self.cp >= 0:
            dl, o = rvar(rest)
            if dl > 0:
                dec = zlib.decompress(rest[o:])
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def rs(self, d, o=0):
        l, o = rvar(d, o); return d[o:o+l].decode(), o+l

    def run(self):
        self.connect()

        # Handshake + Login Start
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        # LOGIN
        while True:
            pid, pl = self.recv()
            if pid == 0x00:
                r, _ = self.rs(pl)
                print(f"[!] Rate limited: {r[:60]}", flush=True)
                self.sock.close(); return False
            if pid == 0x02:
                self.send_pkt(0x03)  # Login Acknowledged
                break
            elif pid == 0x03:
                self.cp, _ = rvar(pl)
            elif pid == 0x04:
                m, o = rvar(pl, 1); c, o = self.rs(pl, o)
                self.send_pkt(0x02, wvar(m) + wvar(0))

        # CONFIG state
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            pid, pl = self.recv()
            if pid == 0x03: break
            elif pid == 0x04: self.send_pkt(0x04, pl)
            elif pid == 0x05: self.send_pkt(0x05, pl)
            elif pid == 0x0E: self.send_pkt(0x07, wvar(0))
            elif pid == 0x12:  # AuthMe
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x00'
                self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13: self.send_pkt(0x09)
            elif pid == 0x02:  # Config Disconnect (kick)
                try:
                    r, _ = self.rs(pl)
                    print(f"[!] Config kick: {r[:200]}", flush=True)
                except: print(f"[!] Config kick (no text)", flush=True)
                return False
            elif pid == 0x11: pass

        # PLAY state
        self.send_pkt(0x03)
        self.sock.settimeout(1)  # short timeout so command scheduler can run
        print("[*] In PLAY", flush=True)

        loaded = False
        cmds = ['balance', 'tradebook help', 'tradebook list']
        ci = 0
        t0 = time.time()
        msgs = []
        last_action = time.time()

        # Start tick-end heartbeat thread
        import threading
        running = True
        def heartbeat():
            while running:
                try: self.send_pkt(0x0D)  # tick_end
                except: break
                time.sleep(0.5)
        th = threading.Thread(target=heartbeat, daemon=True)
        th.start()

        while True:
            now = time.time()

            try:
                pid, pl = self.recv()
                if pid is None: break
            except socket.timeout:
                pid, pl = None, None  # timeout is normal, allows command scheduler to run
            except: break

            # Handle no-packet case (timeout)
            if pid is None:
                pass
            elif pid == 0x2C:  # Keep Alive
                self.send_pkt(0x1C, pl)
            elif pid == 0x31:  # Login/Join
                if not loaded:
                    self.send_pkt(0x2C)  # Player Loaded (empty payload)
                    self.send_pkt(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
            elif pid == 0x48:  # Position
                self.send_pkt(0x00, wvar(0))  # Accept Teleport (varint 0 = teleport id)
            elif pid == 0x20:  # Disconnect
                try:
                    r, _ = self.rs(pl)
                    print(f"[KICK] {r[:200]}", flush=True)
                except:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: print(f"[KICK] {txt[:200]}", flush=True)
                    else: print(f"[KICK] no text, hex={pl[:60].hex()}", flush=True)
                break
            elif pid == 0x79:  # System Chat
                if not loaded:
                    loaded = True  # Paper may not send login packet; system_chat means we're in PLAY
                    self.send_pkt(0x2C)
                    self.send_pkt(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[C] {txt[:400]}", flush=True)
                except: print(f"[C RAW] pid=0x79 hex={pl[:60].hex()}", flush=True)
            elif pid == 0x6E:  # Title/Action Bar
                try:
                    ttype, o = rvar(pl)
                    node, _ = parse_nbt(pl, o, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[A] {txt[:400]}", flush=True)
                except: pass
            elif pid in (0x3B, 0x0E): pass  # Open Screen
            elif pid in (0x76,):  # Config start
                print("[*] Back to config", flush=True); break
            elif pid == 0x23: pass  # Block update
            elif pid == 0x24: pass  # Tick
            elif pid == 0x16: pass  # keep alive 2
            else:
                # Debug unknown packets
                print(f"[?] pid=0x{pid:02x} len={len(pl)}", flush=True)

            # Send commands — use PROTOCOL 775 FORMAT with timestamps
            if ci < len(cmds) and now - t0 > 3 + ci * 5:
                cmd = cmds[ci]
                print(f">>> /{cmd} (t={now-t0:.0f}s)", flush=True)
                ts = int(time.time() * 1000)
                # Protocol 775 SERVERBOUND_CHAT_COMMAND format:
                # command string (no /), timestamp (long), salt (long),
                # argumentSignatures (varint count), messageCount (varint), acknowledged (BitSet)
                m = wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                self.send_pkt(0x07, m)
                ci += 1
                last_action = now

            if ci >= len(cmds) and now - t0 > 50:
                break
            if now - last_action > 30:
                break

        running = False
        self.sock.close()
        print(f"\n=== {len(msgs)} msgs ===", flush=True)
        for m in msgs: print(f"  {m[:300]}", flush=True)

        # Look for flag or balance
        for m in msgs:
            if 'flag' in m.lower() or 'sekai' in m.lower() or 'tbctf' in m.lower():
                print(f"\n*** FLAG FOUND: {m} ***", flush=True)
                return True
        return len(msgs) > 5


if __name__ == "__main__":
    s = Solver(0)
    s.run()
