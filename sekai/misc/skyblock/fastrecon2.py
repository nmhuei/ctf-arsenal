"""
SEKAI CTF Skyblock - Fast Recon Bot
Sends all commands immediately after loading, before the 30s timeout.
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

def fast_recon(cmds, name_suffix=''):
    """Connect, register, load, send commands, collect responses within timeout."""
    ts = int(time.time() % 100000)
    uname = f"Z{ts}{name_suffix}"
    pwd = f"pw{ts}"
    uid = uuid.uuid4()
    cp = -1

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((HOST, PORT))

    def send(pid, data=b''):
        nonlocal cp
        raw = wvar(pid) + data
        if cp >= 0:
            if len(raw) >= cp:
                c = zlib.compress(raw); f = wvar(len(raw)) + c
            else: f = wvar(0) + raw
            sock.sendall(wvar(len(f)) + f)
        else: sock.sendall(wvar(len(raw)) + raw)

    def recv():
        d = b''
        while True:
            b = sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        l, _ = rvar(d)
        rest = b''
        while len(rest) < l:
            c = sock.recv(l - len(rest))
            if not c: return None, None
            rest += c
        if cp >= 0:
            dl, o = rvar(rest)
            if dl > 0:
                try: dec = zlib.decompress(rest[o:])
                except: return None, None
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    # Login
    send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
    send(0x00, wstr(uname) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))
    while True:
        pid, pl = recv()
        if pid is None or pid == 0x00: return None
        if pid == 0x02: send(0x03); break
        elif pid == 0x03: cp, _ = rvar(pl)
        elif pid == 0x04: m, o = rvar(pl, 1); send(0x02, wvar(m) + wvar(0))

    # Config
    send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
    while True:
        pid, pl = recv()
        if pid is None or pid == 0x02: return None
        if pid == 0x03: break
        elif pid == 0x04: send(0x04, pl)
        elif pid == 0x05: send(0x05, pl)
        elif pid == 0x0E: send(0x07, wvar(0))
        elif pid == 0x12:
            nbt = b'\x0a\x00\x00' + b'\x08\x00\x08password' + struct.pack('>H', len(pwd)) + pwd.encode()
            nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(pwd)) + pwd.encode() + b'\x00'
            send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
        elif pid == 0x13: send(0x09)

    # PLAY
    send(0x03)
    msgs = []
    loaded = False
    commands_sent = False
    t0 = time.time()

    while time.time() - t0 < 28:  # Must finish before 30s kick
        try: pid, pl = recv()
        except socket.timeout: pid = None
        except: break

        if pid is None: pass
        elif pid == 0x2C: send(0x1C, pl)  # keep_alive
        elif pid == 0x31:  # login/join
            if not loaded:
                send(0x2C)  # player_loaded
                send(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                loaded = True
                # Send ALL commands immediately
                for cmd in cmds:
                    ts = int(time.time() * 1000)
                    m = wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                    send(0x07, m)
                commands_sent = True
                print(f"  [*] {uname}: {len(cmds)} commands sent", flush=True)
        elif pid == 0x48: send(0x00, wvar(0))
        elif pid == 0x20: break  # kick
        elif pid == 0x79:
            try:
                node, _ = parse_nbt(pl, 0, True)
                txt = chat_text(node).strip() if node else ''
                if txt: msgs.append(txt)
            except: pass
        elif pid == 0x6E:
            try:
                ttype, o = rvar(pl)
                node, _ = parse_nbt(pl, o, True)
                txt = chat_text(node).strip() if node else ''
                if txt: msgs.append(txt)
            except: pass

        # Keep sending tick_end
        if loaded and int(time.time() * 2) % 2 == 0:
            send(0x24, b'\x00' * 8)

    sock.close()
    return msgs

if __name__ == "__main__":
    # Phase 1: Get tradebook list
    print("=== Phase 1: Tradebook list ===", flush=True)
    msgs1 = fast_recon(['balance', 'tradebook help', 'tradebook list'])
    if msgs1:
        for m in msgs1: print(f"  {m}", flush=True)

        # Extract items
        items = set()
        for m in msgs1:
            for match in re.findall(r'\[([A-Za-z0-9_ ]+)\]', m):
                item = match.strip().lower().replace(' ', '_')
                if item and item != 'id':
                    items.add(item)

        print(f"\n=== Found {len(items)} items ===", flush=True)
        for item in sorted(items)[:10]:
            print(f"  {item}", flush=True)

        # Phase 2: Probe these items
        if items:
            time.sleep(2)
            print(f"\n=== Phase 2: Probing items ===", flush=True)
            probe_cmds = [f'tradebook info {item}' for item in sorted(items)]
            msgs2 = fast_recon(probe_cmds)
            if msgs2:
                for m in msgs2: print(f"  {m}", flush=True)

    # Check for flag in all collected messages
    all_msgs = (msgs1 or []) + (msgs2 or [])
    for m in all_msgs:
        low = m.lower()
        if any(x in low for x in ['sekai', 'flag', 'tbctf', 'ctf{']):
            print(f"\n*** FLAG: {m} ***", flush=True)
            with open('/tmp/flag.txt', 'w') as f: f.write(m)
