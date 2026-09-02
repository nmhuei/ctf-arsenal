"""
SEKAI CTF 2026 — Skyblock Solver
Minecraft 26.1.2 (Protocol 775) - Paper

Full reconnaissance and flag extraction.
"""
import socket, struct, time, uuid, zlib, re, threading

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

class Solver:
    def __init__(self, suffix=""):
        ts = int(time.time() % 100000)
        self.uname = f"S{ts}{suffix}"
        self.pwd = f"pw{ts}"
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []
        self.loaded = False

    def send_raw(self, data):
        if self.cp >= 0:
            if len(data) >= self.cp:
                c = zlib.compress(data); f = wvar(len(data)) + c
            else: f = wvar(0) + data
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(data)) + data)

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
                try: dec = zlib.decompress(rest[o:])
                except: return None, None
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def rs(self, d, o=0):
        l, o = rvar(d, o); return d[o:o+l].decode(errors='replace'), o+l

    def send_cmd(self, cmd):
        """Send command via chat_command with protocol 775 format."""
        ts = int(time.time() * 1000)
        m = wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
        self.send_pkt(0x07, m)

    def run(self, commands=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        print(f"[*] {self.uname} connecting...", flush=True)

        # Handshake + Login Start
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        # LOGIN
        while True:
            pid, pl = self.recv()
            if pid is None or pid == 0x00: print(f"[!] Login failed", flush=True); return
            if pid == 0x02:
                self.send_pkt(0x03)
                break
            elif pid == 0x03: self.cp, _ = rvar(pl)
            elif pid == 0x04: m, o = rvar(pl, 1); self.send_pkt(0x02, wvar(m) + wvar(0))

        # CONFIG state
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            pid, pl = self.recv()
            if pid is None or pid == 0x02: print(f"[!] Config kick", flush=True); return
            if pid == 0x03: break  # finish_configuration
            elif pid == 0x04: self.send_pkt(0x04, pl)
            elif pid == 0x05: self.send_pkt(0x05, pl)
            elif pid == 0x0E: self.send_pkt(0x07, wvar(0))
            elif pid == 0x12:  # AuthMe form
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x00'
                self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13: self.send_pkt(0x09)

        # PLAY state
        self.send_pkt(0x03)
        self.sock.settimeout(1)
        print("[*] In PLAY", flush=True)

        if commands is None:
            commands = ['help', 'balance', 'tradebook help', 'tradebook list',
                        'shop', 'leaderboard', 'baltop', 'island', 'hub']

        loaded = False
        ci = 0
        t0 = time.time()
        msgs = []
        last_action = time.time()

        # Heartbeat thread
        running = True
        def heartbeat():
            while running:
                try: self.send_pkt(0x0D)
                except: break
                time.sleep(0.5)
        th = threading.Thread(target=heartbeat, daemon=True)
        th.start()

        extra_cmds = []  # Additional commands discovered during recon
        extra_ci = 0

        while True:
            now = time.time()

            try:
                pid, pl = self.recv()
                if pid is None: break
            except socket.timeout:
                pid, pl = None, None
            except: break

            if pid is None:
                pass
            elif pid == 0x2C:  # Keep Alive
                self.send_pkt(0x1C, pl)
            elif pid == 0x31:  # Login/Join
                if not loaded:
                    self.send_pkt(0x2C)
                    self.send_pkt(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
            elif pid == 0x48:  # Position
                self.send_pkt(0x00, wvar(0))
            elif pid == 0x20:  # Disconnect
                try:
                    r, _ = self.rs(pl)
                    print(f"[KICK] {r[:200]}", flush=True)
                except:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: print(f"[KICK] {txt[:200]}", flush=True)
                break
            elif pid == 0x79:  # System Chat
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[C] {txt[:500]}", flush=True)
                except: pass
            elif pid == 0x6E:  # Title/Action Bar
                try:
                    ttype, o = rvar(pl)
                    node, _ = parse_nbt(pl, o, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[A] {txt[:400]}", flush=True)
                except: pass
            elif pid in (0x3B, 0x0E): pass  # Open Screen
            elif pid in (0x76,): print("[*] Back to config", flush=True); break
            elif pid == 0x55:  # action_bar
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[A] {txt[:300]}", flush=True)
                except: pass
            elif pid in (0x23, 0x24, 0x16, 0x63, 0x53, 0x2D, 0x10, 0x04, 0x05): pass

            # Send main commands
            if ci < len(commands) and now - t0 > 3 + ci * 5:
                cmd = commands[ci]
                print(f">>> /{cmd}", flush=True)
                self.send_cmd(cmd)
                ci += 1
                last_action = now

            # Send extra commands (item queries)
            if ci >= len(commands) and extra_ci < len(extra_cmds) and now - last_action > 3:
                cmd = extra_cmds[extra_ci]
                print(f">>> /{cmd}", flush=True)
                self.send_cmd(cmd)
                extra_ci += 1
                last_action = now

            # Check for items in tradebook list to query
            for msg in msgs[-5:]:
                if '[ID:' in msg and len(extra_cmds) == 0:
                    # Found tradebook items, extract item names
                    items_found = set()
                    for line in msgs:
                        m = re.search(r'\[([A-Za-z0-9_ ]+)\]', line)
                        if m:
                            item = m.group(1).strip().lower().replace(' ', '_')
                            if item and item not in ('id', 'id:'):
                                items_found.add(item)
                    for item in list(items_found)[:20]:
                        extra_cmds.append(f'tradebook info {item}')
                    print(f"[+] Added {len(items_found)} items to query", flush=True)

            if ci >= len(commands) and extra_ci >= len(extra_cmds) and now - t0 > 60:
                break
            if ci >= len(commands) and extra_ci >= len(extra_cmds) and now - last_action > 15:
                break
            if now - t0 > 90:
                break

        running = False
        self.sock.close()
        print(f"\n=== {len(msgs)} messages ===", flush=True)
        for m in msgs: print(f"  {m[:300]}", flush=True)

        # Search for flag
        for m in msgs:
            low = m.lower()
            if 'sekai' in low or 'flag' in low or 'tbctf' in low or 'ctf{' in low:
                print(f"\n*** FLAG: {m} ***", flush=True)
                return m

        return msgs


def extract_items(msgs):
    """Parse tradebook list to extract item listings."""
    items = {}
    for m in msgs:
        # "[ID:1] [Diamond] x64 for $100 - /tradebook buy 1"
        match = re.search(r'\[ID:(\d+)\]\s+\[(.+?)\]\s+x(\d+)\s+for\s+\$?(\d+)', m)
        if match:
            item_id = int(match.group(1))
            item_name = match.group(2).strip()
            amount = int(match.group(3))
            price = int(match.group(4))
            if item_name not in items:
                items[item_name] = []
            items[item_name].append({'id': item_id, 'price': price, 'amount': amount, 'raw': m})
    return items


if __name__ == "__main__":
    import sys
    suffix = sys.argv[1] if len(sys.argv) > 1 else ''

    s = Solver(suffix)
    result = s.run()

    if result and isinstance(result, list):
        items = extract_items(result)
        print(f"\n=== Tradebook Items Found: {len(items)} ===", flush=True)
        for name, listings in sorted(items.items()):
            prices = [l['price'] for l in listings]
            print(f"  {name}: {', '.join(f'${p}' for p in prices)}", flush=True)
