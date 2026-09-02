#!/usr/bin/env python3
"""
Fast recon bot for SEKAICTF Minecraft Skyblock.
Connects, sends commands quickly, captures all output.
"""
import socket, struct, time, uuid, zlib, threading, json

HOST, PORT = "skyblock.chals.sekai.team", 25565
PV = 775  # Protocol version for 26.1.2

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

# === NBT Parser (minimal, for text chat) ===
def parse_nbt(data, o=0, anon=False, depth=0):
    if depth > 30 or o >= len(data): return None, o
    tt = data[o]; o += 1
    if tt == 0: return ('end', ''), o
    name = ''
    if not anon:
        if o + 2 > len(data): return None, o
        nl = struct.unpack('>H', data[o:o+2])[0]; o += 2
        if nl: name = data[o:o+nl].decode(errors='replace'); o += nl
    if tt == 0x08:  # String
        vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
        v = data[o:o+vl].decode(errors='replace'); o += vl
        return ('s', name, v), o
    elif tt == 0x0a:  # Compound
        fields = {}
        while o < len(data) and data[o] != 0:
            r, o = parse_nbt(data, o, False, depth+1)
            if r and r[1]: fields[r[1]] = r
        if o < len(data) and data[o] == 0: o += 1
        return ('c', name, fields), o
    elif tt == 0x09:  # List
        lt = data[o]; ll = struct.unpack('>I', data[o+1:o+5])[0]; o += 5
        items = []
        for _ in range(ll):
            if lt == 0x08:
                vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                items.append(data[o:o+vl].decode(errors='replace')); o += vl
            elif lt == 0x0a:
                fields = {}
                while o < len(data) and data[o] != 0:
                    r, o = parse_nbt(data, o, False, depth+1)
                    if r and r[1]: fields[r[1]] = r
                if o < len(data) and data[o] == 0: o += 1
                items.append(fields)
            else: break
        return ('l', name, items), o
    return None, o

def chat_text(node):
    if node is None: return ''
    t, name, val = node
    if t == 's': return val if name in ('text', 'translate', '') else ''
    elif t == 'c':
        parts = []
        for fval in val.values():
            p = chat_text(fval)
            if p: parts.append(p)
        return ''.join(parts)
    elif t == 'l':
        return ''.join(chat_text(i) if isinstance(i, tuple) else str(i) for i in val)
    return ''

class FastBot:
    def __init__(self, name_suffix):
        self.uname = f"Bot{int(time.time())%10000}{name_suffix}"
        self.pwd = "pw" + str(int(time.time())%10000)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []
        self.running = False

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

    def recv(self, timeout=15):
        self.sock.settimeout(timeout)
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

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        # Handshake + Login Start
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        # LOGIN state
        while True:
            pid, pl = self.recv()
            if pid is None: return False
            if pid == 0x00:  # Disconnect
                try:
                    r, _ = rvar(pl)
                    rest = pl[1:]
                    msg = rest.decode(errors='replace')
                    print(f"[!] Login rejected: {msg[:100]}", flush=True)
                except: pass
                return False
            elif pid == 0x02:  # Login Success
                self.send_pkt(0x03)  # Login Acknowledged
                break
            elif pid == 0x03:  # Compression
                self.cp, _ = rvar(pl)
            elif pid == 0x04:  # Login Plugin Request
                m, o = rvar(pl, 1)
                c, o = rvar(pl, o)
                # Try to read plugin channel
                ch = pl[o:o+c].decode(errors='replace') if c > 0 else ''
                self.send_pkt(0x02, wvar(m) + wvar(0))

        print(f"[+] {self.uname}: CONFIG state", flush=True)

        # CONFIG state - Send client info
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        while True:
            pid, pl = self.recv(5)
            if pid is None:
                print(f"[!] {self.uname}: config timeout", flush=True)
                return False

            if pid == 0x03:  # Finish Config
                break
            elif pid == 0x04:  # Keep Alive
                self.send_pkt(0x04, pl)
            elif pid == 0x05:  # Ping
                self.send_pkt(0x05, pl)
            elif pid == 0x0E:  # Update Tags
                self.send_pkt(0x07, wvar(0))
            elif pid == 0x12:  # AuthMe plugin message
                # Extract channel name
                ch_name, o = rvar(pl)
                ch = pl[o:o+ch_name].decode(errors='replace') if ch_name > 0 else ''
                pl_len, o = rvar(pl, o+ch_name)
                pl_data = pl[o:o+pl_len]
                print(f"[AuthMe] channel={ch} data={pl_data[:60].hex()}", flush=True)
                if 'prejoin' in ch or 'register' in ch:
                    # Register/Login
                    nbt = b'\x0a\x00\x00'
                    nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                    nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                    nbt += b'\x00'
                    self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
                    print(f"[+] {self.uname}: sent register pwd={self.pwd}", flush=True)
            elif pid == 0x13:  # AuthMe require response
                self.send_pkt(0x09)
            elif pid == 0x02:  # Disconnect
                try:
                    r, _ = rvar(pl)
                    rest = pl[1:]
                    msg = rest.decode(errors='replace')
                    print(f"[!] Config kick: {msg[:200]}", flush=True)
                except: pass
                return False
            elif pid == 0x11:  # Transfer
                pass

        print(f"[+] {self.uname}: PLAY state", flush=True)

        # PLAY state - send tick end, client load, etc.
        self.send_pkt(0x03)  # finish play config
        self.sock.settimeout(1)

        return True

    def send_chat_command(self, cmd):
        """Send /command with protocol 775 format."""
        ts = int(time.time() * 1000)
        m = wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
        self.send_pkt(0x07, m)

    def send_chat_msg(self, msg):
        """Send normal chat message."""
        ts = int(time.time() * 1000)
        m = wstr(msg) + struct.pack('>q', ts) + struct.pack('>q', 0)
        m += wvar(0) + wvar(0) + bytes(3) + struct.pack('B', 0)
        self.send_pkt(0x08, m)

    def run_recon(self):
        """Run full recon sequence."""
        if not self.connect():
            return False

        # Start heartbeat
        running = True
        def hb():
            while running:
                try: self.send_pkt(0x0D)
                except: break
                time.sleep(0.5)
        threading.Thread(target=hb, daemon=True).start()

        commands = [
            '/help',
            '/balance',
            '/tradebook help',
            '/tradebook list',
        ]

        ci = 0
        t0 = time.time()

        while True:
            now = time.time()
            try:
                pid, pl = self.recv(1)
                if pid is None: break
            except socket.timeout:
                pid = None
            except:
                break

            if pid is None:
                pass
            elif pid == 0x2C:  # Keep Alive
                self.send_pkt(0x1C, pl)
            elif pid == 0x31:  # Login/Join Game
                self.send_pkt(0x2C)  # Player Loaded
                self.send_pkt(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
            elif pid == 0x48:  # Position
                self.send_pkt(0x00, wvar(0))
            elif pid == 0x20:  # Disconnect
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: print(f"[KICK] {txt[:200]}", flush=True)
                    else: print(f"[KICK] hex={pl[:60].hex()}", flush=True)
                except: pass
                running = False
                break
            elif pid == 0x79:  # System Chat
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt:
                        # Strip color codes
                        import re as rer
                        txt = rer.sub(r'\xa7.', '', txt)
                        self.msgs.append(txt)
                        print(f"[C] {txt[:500]}", flush=True)
                except:
                    pass
            elif pid == 0x6E:  # Title
                try:
                    ttype, o = rvar(pl)
                    node, _ = parse_nbt(pl, o, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt:
                        import re as rer
                        txt = rer.sub(r'\xa7.', '', txt)
                        self.msgs.append(txt)
                        print(f"[T] {txt[:300]}", flush=True)
                except: pass
            elif pid == 0x3F:  # Player Chat
                try:
                    o = 0
                    gi, o = rvar(pl, o); o += 1  # skip sender
                    o += 16  # skip UUID
                    idx, o = rvar(pl, o) if o < len(pl) else (0, o)
                    sig_f = pl[o] if o < len(pl) else 0; o += 1
                    if sig_f and o < len(pl):
                        try:
                            sl, o = rvar(pl, o)
                            hlen, o = rvar(pl, o) if o < len(pl) else (0, o)
                            o += hlen + 32
                        except: pass
                    msg_len, o = rvar(pl, o) if o < len(pl) else (0, o)
                    if o + msg_len <= len(pl):
                        msg = pl[o:o+msg_len].decode(errors='replace')
                        import re as rer
                        msg = rer.sub(r'\xa7.', '', msg)
                        if msg: self.msgs.append(msg); print(f"[P] {msg[:400]}", flush=True)
                except: pass
            elif pid == 0x76:  # Config start
                print("[*] Back to CONFIG", flush=True)
                break

            # Send commands on schedule
            if ci < len(commands) and now - t0 > 3 + ci * 4:
                cmd = commands[ci]
                print(f">>> /{cmd}", flush=True)
                self.send_chat_command(cmd)
                ci += 1

            # Timeout after 45 seconds
            if now - t0 > 45:
                break

        running = False
        self.sock.close()

        print(f"\n{'='*60}", flush=True)
        print(f"RESULTS ({len(self.msgs)} messages):", flush=True)
        print('='*60, flush=True)
        for m in self.msgs:
            print(m, flush=True)

        return True


if __name__ == "__main__":
    import sys
    suffix = sys.argv[1] if len(sys.argv) > 1 else ''
    bot = FastBot(suffix)
    bot.run_recon()
