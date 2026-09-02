#!/usr/bin/env python3
"""Probe chat PID — no keep_alive, one PID at a time"""
import socket, struct, time, uuid, zlib
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

cp = -1
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(15)
sock.connect((HOST, PORT))
uid = uuid.uuid4(); ts = int(time.time())
name = f"Pb{ts%10000}"; pwd = f"pw{ts%10000}"

def send(pid, data=b''):
    global cp
    r = wvar(pid) + data
    if cp >= 0:
        if len(r) >= cp: c = zlib.compress(r); f = wvar(len(r)) + c
        else: f = wvar(0) + r
        sock.sendall(wvar(len(f)) + f)
    else: sock.sendall(wvar(len(r)) + r)

def recv():
    global cp
    d = b''
    while True:
        b = sock.recv(1)
        if not b: return None, None
        d += b
        if not (b[0] & 0x80): break
    pl, _ = rvar(d); rt = b''
    while len(rt) < pl:
        c = sock.recv(pl - len(rt))
        if not c: return None, None
        rt += c
    if cp >= 0:
        dl, o = rvar(rt)
        if dl > 0: dec = zlib.decompress(rt[o:]); p, o2 = rvar(dec); return p, dec[o2:]
        else: p, o2 = rvar(rt, o); return p, rt[o2:]
    else: p, o = rvar(rt); return p, rt[o:]

# Login
send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
send(0x00, wstr(name) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))
while True:
    p, pl = recv()
    if p == 0x00: print("BLOCKED"); exit()
    if p == 0x02: send(0x03); break
    elif p == 0x03: cp, _ = rvar(pl)
    elif p == 0x04: m, o = rvar(pl, 1); send(0x02, wvar(m) + wvar(0))

# Config
send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
while True:
    p, pl = recv()
    if p == 0x03: break
    elif p == 0x04: send(0x04, pl)
    elif p == 0x05: send(0x05, pl)
    elif p == 0x0E:
        cnt, o = rvar(pl); resp = b''
        for _ in range(cnt):
            l, o = rvar(pl, o); ns = pl[o:o+l].decode(); o += l
            l, o = rvar(pl, o); n = pl[o:o+l].decode(); o += l
            l, o = rvar(pl, o); v = pl[o:o+l].decode(); o += l
            resp += wstr(ns) + wstr(n) + wstr(v)
        send(0x07, wvar(cnt) + resp)
    elif p == 0x12:
        nbt = b'\x0a\x00\x00'
        nbt += b'\x08\x00\x08password' + struct.pack('>H', len(pwd)) + pwd.encode()
        nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(pwd)) + pwd.encode() + b'\x00'
        send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01' + nbt)) + b'\x01' + nbt)
    elif p == 0x13: send(0x09)
    elif p == 0x02: print("CFGKICK"); exit()

print("+Connected", flush=True)

# PLAY
send(0x03)
sock.settimeout(0.5)
t0 = time.time(); loaded = False; msgs = []

def parse_chat(pl):
    if not pl: return ""
    def _scan(d, o):
        r = []
        while o < len(d):
            tt = d[o]
            if tt == 0: return "".join(r), o + 1
            o += 1
            if o + 2 > len(d): break
            nl = struct.unpack('>H', d[o:o+2])[0]
            nm = d[o+2:o+2+nl].decode(errors='replace') if nl else ''
            o += 2 + nl
            if tt == 0x08:
                if o + 2 > len(d): break
                sl = struct.unpack('>H', d[o:o+2])[0]
                if o + sl + 2 > len(d): break
                val = d[o+2:o+2+sl].decode(errors='replace'); o += 2 + sl
                if nm in ('text', ''): r.append(val)
            elif tt == 0x09:
                if o + 5 > len(d): break
                lt, ll = d[o], struct.unpack('>I', d[o+1:o+5])[0]; o += 5
                for _ in range(ll):
                    if lt == 0x0a: s, o = _scan(d, o); r.append(s)
                    elif lt == 0x08:
                        if o + 2 > len(d): break
                        sl = struct.unpack('>H', d[o:o+2])[0]
                        if o + sl + 2 > len(d): break
                        r.append(d[o+2:o+2+sl].decode(errors='replace')); o += 2 + sl
                    else: break
            elif tt == 0x0a: s, o = _scan(d, o); r.append(s)
            else: break
        return "".join(r), o
    try: r, _ = _scan(pl, 1); return r.replace('\xa7', '').strip()
    except: return ""

# Init PLAY
while time.time() - t0 < 10:
    try: p, pl = recv()
    except socket.timeout: continue
    except: break
    if p == 0x31 and not loaded:
        send(0x2C)
        send(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        loaded = True
        print("+PLAY init", flush=True)
        break

# Now probe each PID from 0x01 to 0x30
# Skip: 0x00(teleport_confirm), 0x0E(settings), 0x1B(keep_alive), 0x2C(player_loaded)
skip = {0x00, 0x0E, 0x1B, 0x2C, 0x31, 0x20, 0x46, 0x79, 0x3d}

# Only test innocent-looking PIDs that could be chat
# Paper uses different ID mapping than vanilla
# Try all from 0x01-0x30

probe_pids = [i for i in range(0x01, 0x31) if i not in skip]
# Prioritize PIDs near where chat usually lives
priority = [0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0f, 0x10]
probe_pids = priority + [p for p in probe_pids if p not in priority]

fmt_idx = 0
formats = [
    ("string", lambda cmd: wstr(cmd)),
    ("string+ts+salt", lambda cmd: wstr(cmd) + struct.pack('>q', int(time.time()*1000)) + struct.pack('>q', 0)),
    ("full_signed", lambda cmd: wstr(cmd) + struct.pack('>q', int(time.time()*1000)) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00\x00\x00' + struct.pack('B', 0)),
    ("message", lambda cmd: wstr("/"+cmd) + struct.pack('>q', int(time.time()*1000)) + struct.pack('>q', 0) + b'\x00' + wvar(0) + b'\x00\x00\x00' + struct.pack('B', 0)),
]

for pid in probe_pids:
    for fname, fbuilder in formats:
        # Wait for a gap in traffic
        time.sleep(0.8)
        now = time.time() - t0

        # Send command
        try:
            payload = fbuilder("coins")
            send(pid, payload)
            print(f"[{now:.1f}] PID=0x{pid:02x} fmt={fname}", flush=True)
        except Exception as e:
            print(f"[!] 0x{pid:02x} {fname} send error: {e}", flush=True)
            continue

        # Wait for response
        t1 = time.time()
        got_response = False
        while time.time() - t1 < 1.0:
            try: p, pl = recv()
            except socket.timeout: break
            except: break

            if p == 0x20:
                txt = parse_chat(pl)
                print(f"[KICK] @{time.time()-t0:.1f} after 0x{pid:02x}: {txt[:60]}", flush=True)
                got_response = True
                break
            elif p == 0x79:
                txt = parse_chat(pl)
                if txt and len(txt) > 3:
                    # Don't show initial welcome again
                    if txt not in msgs or txt not in ('Welcome to Skyblock', 'Commands', 'Build your island, harvest resources, earn coins, and level skills.', 'Harvest crops or mine public ores for skill XP and coins.'):
                        msgs.append(txt)
                        print(f"[CHAT] @{time.time()-t0:.1f} after 0x{pid:02x}: {txt[:120]}", flush=True)
                        got_response = True
                    else:
                        # If got a known msg, still record that PID got a response
                        got_response = True

        if not got_response:
            pass  # No news is good news - PID accepted packet silently

print(f"\n{'='*50}", flush=True)
print(f"Total time: {time.time()-t0:.1f}s", flush=True)
for m in msgs:
    if m not in ('Welcome to Skyblock', 'Commands'):
        print(f"  MSG: {m[:150]}", flush=True)
sock.close()
