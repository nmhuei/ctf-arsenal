#!/usr/bin/env python3
"""Debug Paper 26.1.2 PLAY state - track all packet timing"""
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

def rs(d, o=0):
    l, o = rvar(d, o)
    return d[o:o+l].decode(), o+l

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(30); sock.connect((HOST, PORT))
cp = -1
uid = uuid.uuid4()
name = "U" + str(int(time.time()) % 10000)
pwd = "pw" + str(int(time.time()) % 10000)

def send_raw(data):
    global cp
    if cp >= 0:
        if len(data) >= cp: c = zlib.compress(data); f = wvar(len(data)) + c
        else: f = wvar(0) + data
        sock.sendall(wvar(len(f)) + f)
    else: sock.sendall(wvar(len(data)) + data)

def send_pkt(pid, data=b''): send_raw(wvar(pid) + data)

def recv():
    d = b''
    while True:
        b = sock.recv(1)
        if not b: return None, None
        d += b
        if not (b[0] & 0x80): break
    plen, _ = rvar(d)
    rest = b''
    while len(rest) < plen:
        c = sock.recv(plen - len(rest))
        if not c: return None, None
        rest += c
    if cp >= 0:
        dl, o = rvar(rest)
        if dl > 0: dec = zlib.decompress(rest[o:]); pid, o2 = rvar(dec); return pid, dec[o2:]
        else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
    else: pid, o = rvar(rest); return pid, rest[o:]

# Handshake + Login
send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
send_pkt(0x00, wstr(name) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))
while True:
    pid, pl = recv()
    if pid == 0x00: print("Rejected"); exit()
    if pid == 0x02: send_pkt(0x03); break
    elif pid == 0x03: cp, _ = rvar(pl)
    elif pid == 0x04: mid, o = rvar(pl, 1); send_pkt(0x02, wvar(mid) + wvar(0))
print("[+] Login", flush=True)

# Config
send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
while True:
    pid, pl = recv()
    if pid == 0x03: break
    elif pid == 0x04: send_pkt(0x04, pl)
    elif pid == 0x05: send_pkt(0x05, pl)
    elif pid == 0x0E:
        cnt, o = rvar(pl); resp = b''
        for _ in range(cnt):
            ns, o = rs(pl, o); n, o = rs(pl, o); v, o = rs(pl, o)
            resp += wstr(ns) + wstr(n) + wstr(v)
        send_pkt(0x07, wvar(cnt) + resp)
    elif pid == 0x12:
        print(f"[+] AuthMe pwd={pwd}", flush=True)
        nbt = b'\x0a\x00\x00'
        nbt += b'\x08\x00\x08password' + struct.pack('>H', len(pwd)) + pwd.encode()
        nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(pwd)) + pwd.encode() + b'\x00'
        send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
    elif pid == 0x13: send_pkt(0x09)
    elif pid == 0x02: print("Config kick"); exit()
print("[+] Config done", flush=True)

# PLAY
send_pkt(0x03)
sock.settimeout(0.5)
t0 = time.time()
loaded = False

while True:
    now = time.time()
    try:
        pid, pl = recv()
        if pid is None: break
    except socket.timeout: pid = None
    except: break

    if pid == 0x31 and not loaded:
        loaded = True; print(f"[{now-t0:.2f}] LOGIN -> player_loaded", flush=True); send_pkt(0x21)
    elif pid == 0x2C and len(pl) == 8:
        send_pkt(0x1B, pl)
    elif pid == 0x20:
        print(f"[{now-t0:.2f}] KICK len={len(pl)}", flush=True)
        if len(pl):
            try: msg, _ = rs(pl); print(f"  MSG: {msg[:200]}", flush=True)
            except: print(f"  HEX: {pl[:80].hex()}", flush=True)
        break
    elif pid == 0x79:
        pass  # system_chat
    elif pid is not None:
        print(f"[{now-t0:.2f}] pkt=0x{pid:02x} len={len(pl)}", flush=True)

    if now - t0 > 15: print("[*] Timeout", flush=True); break

sock.close()
print(f"[*] Done: {time.time()-t0:.1f}s", flush=True)
