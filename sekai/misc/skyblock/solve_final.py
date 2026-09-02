"""
SEKAI CTF 2026 — Skyblock Solver (Paper 26.1.2)
Uses Paper-specific packet offsets from working v10 client.
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
    while True: b = d[o]; r |= (b & 0x7F) << s; s += 7; o += 1
    if not (b & 0x80): return r, o
def wstr(s): e = s.encode(); return wvar(len(e)) + e

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
                fields = {}; last_o = o
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
        self.uname = f"B{ts}{suffix}"
        self.pwd = f"pw{ts}"
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []
        self.loaded = False

    def send_raw(self, data):
        if self.cp >= 0:
            if len(data) >= self.cp:
                self.sock.sendall(wvar(len(wvar(len(data)) + zlib.compress(data))) + wvar(len(data)) + zlib.compress(data))
            else:
                self.sock.sendall(wvar(len(wvar(0) + data)) + wvar(0) + data)
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
                dec = zlib.decompress(rest[o:])
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def rs(self, d, o=0):
        l, o = rvar(d, o); return d[o:o+l].decode(), o+l

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        print(f"[*] {self.uname} connecting...", flush=True)

        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        while True:
            pid, pl = self.recv()
            if pid is None or pid == 0x00: print(f"[!] Login failed", flush=True); return
            if pid == 0x02: self.send_pkt(0x03); break
            elif pid == 0x03: self.cp, _ = rvar(pl)
            elif pid == 0x04: m, o = rvar(pl, 1); self.send_pkt(0x02, wvar(m) + wvar(0))

        # CONFIG
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            pid, pl = self.recv()
            if pid is None or pid == 0x02: print(f"[!] Config kick", flush=True); return
            if pid == 0x03: break
            elif pid == 0x04: self.send_pkt(0x04, pl)
            elif pid == 0x05: self.send_pkt(0x05, pl)
            elif pid == 0x0E: self.send_pkt(0x07, wvar(0))
            elif pid == 0x12:
                nbt = b'\x0a\x00\x00' + b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13: self.send_pkt(0x09)

        # PLAY
        self.send_pkt(0x03)
        self.sock.settimeout(1)
        print("[*] In PLAY", flush=True)
        self.loaded = False

        r = True
        def hb():
            while r:
                try:
                    self.send_pkt(0x24, b'\x00' * 8)  # tick_end (Paper)
                    time.sleep(1)
                except: break
        threading.Thread(target=hb, daemon=True).start()

        t0 = time.time()
        msgs = []
        cmds_sent = 0
        all_cmds = ['balance', 'tradebook help', 'tradebook list']
        item_queries = []
        qi = 0

        while time.time() - t0 < 75:
            try: pid, pl = self.recv()
            except socket.timeout: pid = None
            except: break

            if pid is None: pass
            elif pid == 0x2C: self.send_pkt(0x1C, pl)  # keep_alive
            elif pid == 0x31:  # login/join
                if not self.loaded:
                    self.send_pkt(0x2C)  # player_loaded
                    self.send_pkt(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    self.loaded = True
                    print("[+] Loaded!", flush=True)
                    # Send commands immediately
                    for cmd in all_cmds:
                        ts = int(time.time() * 1000)
                        m = wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                        self.send_pkt(0x07, m)
                        cmds_sent += 1
                        print(f">>> /{cmd}", flush=True)
                        time.sleep(0.25)
            elif pid == 0x48: self.send_pkt(0x00, wvar(0))  # position ack
            elif pid == 0x20:
                try:
                    r2, _ = self.rs(pl); print(f"[KICK] {r2[:200]}", flush=True)
                except:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else 'N/A'
                    print(f"[KICK] {txt[:200]}", flush=True)
                    if 'timeout' not in txt.lower():
                        break
                    else:
                        print("[*] Login timeout kicked, reconnecting in new session...", flush=True)
                        break
            elif pid == 0x79:
                try:
                    node, _ = parse_nbt(pl, 0, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[C] {txt[:500]}", flush=True)
                except: pass
            elif pid == 0x6E:
                try:
                    ttype, o = rvar(pl)
                    node, _ = parse_nbt(pl, o, True)
                    txt = chat_text(node).strip() if node else ''
                    if txt: msgs.append(txt); print(f"[A] {txt[:400]}", flush=True)
                except: pass

            # Item queries
            if not item_queries and len(msgs) > 15:
                for m in msgs:
                    for match in re.findall(r'\[([A-Za-z0-9_ ]+)\]', m):
                        item = match.strip().lower().replace(' ', '_')
                        if item not in ('', 'id') and item not in item_queries:
                            item_queries.append(item)
                print(f"[+] Items to probe: {len(item_queries)}", flush=True)

            if item_queries and qi < len(item_queries) and qi < 30:
                item = item_queries[qi]
                ts = int(time.time() * 1000)
                m = wstr(f'tradebook info {item}') + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                self.send_pkt(0x07, m)
                print(f">>> /tradebook info {item} [{qi+1}/{len(item_queries)}]", flush=True)
                qi += 1
                time.sleep(0.5)

        # Done
        r = False
        self.sock.close()

        print(f"\n{'='*60}\n=== {len(msgs)} msgs ===", flush=True)
        for m in msgs: print(f"  {m[:300]}", flush=True)

        for m in msgs:
            low = m.lower()
            if any(x in low for x in ['sekai', 'flag', 'tbctf', 'ctf{']):
                print(f"\n*** FLAG FOUND: {m} ***", flush=True)
                return m
        return msgs

if __name__ == "__main__":
    import sys
    s = Solver(sys.argv[1] if len(sys.argv) > 1 else '')
    s.run()
