#!/usr/bin/env python3
"""
Skyblock Bot v2 — uses final_solve.py flow but sends commands and listens on correct chat PIDs
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

# Chat PIDs (from minecraft-data 26.1.2)
CB_PROFILELESS_CHAT = 0x21
CB_PLAYER_CHAT      = 0x3f
CB_SYSTEM_CHAT      = 0x77
CB_HIDE_MESSAGE     = 0x1f
CB_KICK             = 0x20
CB_LOGIN            = 0x31
CB_POSITION         = 0x46
CB_KEEP_ALIVE       = 0x2c  # 8 bytes = i64

SB_CHAT_COMMAND     = 0x06
SB_PLAYER_LOADED    = 0x2c
SB_KEEP_ALIVE       = 0x1b
SB_TELEPORT_CONFIRM = 0x00
SB_SETTINGS         = 0x0e

def parse_nbt_chat(pl):
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
                        if off + sl + 2 > len(d): break
                        r.append(d[off+2:off+2+sl].decode(errors='replace')); off += 2 + sl
                    else: break
            elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
            else: break
        return "".join(r), off
    try:
        result, _ = _scan(pl, 1)
        return result.replace('\xa7', '').strip()
    except: return ""

def try_connect():
    """Retry until antibot passes"""
    for attempt in range(50):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        try: sock.connect((HOST, PORT))
        except: time.sleep(5); continue

        cp = -1; uid = uuid.uuid4(); ts = int(time.time())
        name = f"SB{ts%10000}"; pwd = f"sb{ts%1000}"

        def send(pid, data=b''):
            nonlocal cp
            r = wvar(pid) + data
            if cp >= 0:
                if len(r) >= cp: c = zlib.compress(r); f = wvar(len(r)) + c
                else: f = wvar(0) + r
                sock.sendall(wvar(len(f)) + f)
            else: sock.sendall(wvar(len(r)) + r)

        def recv():
            nonlocal cp
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
                if dl > 0:
                    dec = zlib.decompress(rt[o:])
                    p, o2 = rvar(dec); return p, dec[o2:]
                else: p, o2 = rvar(rt, o); return p, rt[o2:]
            else: p, o = rvar(rt); return p, rt[o:]

        try:
            # Login
            send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
            send(0x00, wstr(name) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))
            ok = False
            while True:
                p, pl = recv()
                if p == 0x00: break
                if p == 0x02: send(0x03); ok = True; break
                elif p == 0x03: cp, _ = rvar(pl)
                elif p == 0x04: m, o = rvar(pl, 1); send(0x02, wvar(m) + wvar(0))
            if not ok: sock.close(); time.sleep(5); continue

            # Config
            send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
            ok = False
            while True:
                p, pl = recv()
                if p == 0x03: ok = True; break
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
                elif p == 0x02: break
            if not ok: sock.close(); time.sleep(5); continue

            # PLAY
            send(0x03)
            return (sock, send, recv, cp)
        except:
            sock.close()
            time.sleep(5)
            continue
    return None

result = try_connect()
if result is None: print("Failed to connect"); sys.exit(1)
sock, send, recv, cp = result
sock.settimeout(0.5)

t0 = time.time(); loaded = False; ka = 0; cmd_idx = 0
cmds = ["help", "coins", "hub", "is", "sb", "mine", "shop"]  # various commands

chat_msgs = []
unknown_79_count = 0

while time.time() - t0 < 45:
    try:
        sock.settimeout(0.3)
        p, pl = recv()
        if p is None: break
    except socket.timeout:
        now = time.time() - t0
        if loaded and now > 4 and cmd_idx < len(cmds) and now > 4 + cmd_idx * 6:
            # wait 6s between each command
            send(SB_CHAT_COMMAND, wstr(cmds[cmd_idx]))
            print(f"[>] /{cmds[cmd_idx]} @{now:.1f}s", flush=True)
            cmd_idx += 1
            if cmd_idx == 1:
                print("[*] Commands sent. Now waiting for responses...", flush=True)
        continue
    except: break

    dt = time.time() - t0

    if p == CB_LOGIN and not loaded:
        send(SB_PLAYER_LOADED)
        send(SB_SETTINGS, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        loaded = True
        print(f"[+] READY @{dt:.1f}s", flush=True)

    elif p == CB_KEEP_ALIVE and len(pl) == 8:
        ka += 1

    elif p == CB_POSITION and len(pl) < 50:
        tid, o = rvar(pl)
        send(SB_TELEPORT_CONFIRM, wvar(tid))

    # Chat messages — the REAL chat PIDs
    elif p == CB_SYSTEM_CHAT:
        txt = parse_nbt_chat(pl)
        if txt: print(f"[SYS] {txt[:200]}", flush=True); chat_msgs.append(('sys', txt))

    elif p == CB_PROFILELESS_CHAT:
        txt = parse_nbt_chat(pl)
        if txt: print(f"[PLC] {txt[:200]}", flush=True); chat_msgs.append(('plc', txt))

    elif p == CB_PLAYER_CHAT:
        txt = parse_nbt_chat(pl)
        if txt: print(f"[PLA] {txt[:200]}", flush=True); chat_msgs.append(('pla', txt))

    elif p == CB_HIDE_MESSAGE:
        txt = parse_nbt_chat(pl)
        if txt: print(f"[HID] {txt[:200]}", flush=True); chat_msgs.append(('hid', txt))

    elif p == 0x79:
        unknown_79_count += 1

    elif p == CB_KICK:
        try: l, o = rvar(pl, 0); m = pl[o:o+l].decode(errors='replace')
        except: m = repr(pl[:40])
        print(f"[!] KICK @{dt:.1f}s: {m[:120]}", flush=True); break

dur = time.time() - t0
print(f"\n[*] Session: {dur:.1f}s, KA={ka}, chat_msgs={len(chat_msgs)}, 0x79={unknown_79_count}", flush=True)
for t, m in chat_msgs:
    print(f"  [{t}] {m[:150]}", flush=True)

# Check for flag
all_txt = " ".join(m for _, m in chat_msgs)
for kw in ['flag{', 'sekai{', 'SEKAI', 'ctf{', 'TBCTF']:
    if kw in all_txt or kw.lower() in all_txt.lower():
        print(f"\n*** FLAG FOUND: {all_txt} ***", flush=True)

sock.close()
