#!/usr/bin/env python3
"""Test keep_alive and chat command IDs for Paper 26.1.2"""
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
sock.settimeout(30)
sock.connect((HOST, PORT))
cp = -1
uid = uuid.uuid4()
name = "D" + str(int(time.time()) % 1000)

def send_raw(data):
    global cp
    if cp >= 0:
        if len(data) >= cp:
            c = zlib.compress(data)
            f = wvar(len(data)) + c
        else:
            f = wvar(0) + data
        sock.sendall(wvar(len(f)) + f)
    else:
        sock.sendall(wvar(len(data)) + data)

def send_pkt(pid, data=b''):
    send_raw(wvar(pid) + data)

def recv_pkt():
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
        if dl > 0:
            dec = zlib.decompress(rest[o:])
            pid, o2 = rvar(dec)
            return pid, dec[o2:]
        else:
            pid, o2 = rvar(rest, o)
            return pid, rest[o2:]
    else:
        pid, o = rvar(rest)
        return pid, rest[o:]

# Handshake + Login
send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
send_pkt(0x00, wstr(name) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))

while True:
    pid, pl = recv_pkt()
    if pid == 0x00: print("Login reject"); exit()
    if pid == 0x02: send_pkt(0x03); break
    elif pid == 0x03: cp, _ = rvar(pl)
    elif pid == 0x04:
        mid, o = rvar(pl, 1)
        send_pkt(0x02, wvar(mid) + wvar(0))

# Config
send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

while True:
    pid, pl = recv_pkt()
    if pid == 0x03: break
    elif pid == 0x04: send_pkt(0x04, pl)
    elif pid == 0x05: send_pkt(0x05, pl)
    elif pid == 0x0E:
        cnt, o = rvar(pl)
        resp = b''
        for _ in range(cnt):
            ns, o = rs(pl, o)
            n, o = rs(pl, o)
            v, o = rs(pl, o)
            resp += wstr(ns) + wstr(n) + wstr(v)
        send_pkt(0x07, wvar(cnt) + resp)
    elif pid == 0x12:
        pwd = "pw00"
        nbt = b'\x0a\x00\x00'
        nbt += b'\x08\x00\x08password' + struct.pack('>H', len(pwd)) + pwd.encode()
        nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(pwd)) + pwd.encode() + b'\x00'
        send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
    elif pid == 0x13: send_pkt(0x09)

# PLAY
send_pkt(0x03)
sock.settimeout(0.5)
print("[+] PLAY", flush=True)

t0 = time.time()
ka_id = None
ka_count = 0
attempt_sent = False
alive = True

# Track which PID we're testing for keep_alive response
ka_test_ids = {'to_client': 0x2C}

# Try KA with different C->S ids
cs_ka_ids = [0x1B, 0x1C, 0x1D, 0x2B, 0x2C]
cmd_ids = [0x06, 0x07, 0x08, 0x09]

while time.time() - t0 < 15:
    try:
        pid, pl = recv_pkt()
        if pid is None: break
    except socket.timeout:
        pid = None
    except: break

    if pid is None:
        if ka_id is not None and ka_count > 0:
            # Try responding with ONE KA ID per interval
            for cs_pid in cs_ka_ids:
                send_pkt(cs_pid, struct.pack('>q', ka_id))

        if not attempt_sent and time.time() - t0 > 2:
            # Send player loaded
            send_pkt(0x2B)
            print("  sent player_loaded (0x2B)", flush=True)

            # Send commands with all possible IDs
            for cmd_pid in cmd_ids:
                m = wstr("coins") + struct.pack('>q', int(time.time()*1000))
                m += struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00'
                send_pkt(cmd_pid, m)
                print(f"  sent /coins at 0x{cmd_pid:02x}", flush=True)
            attempt_sent = True
    elif pid == 0x20:
        try:
            msg, _ = rs(pl)
            print(f"[KICK] {msg[:200]}", flush=True)
        except: print(f"[KICK] hex={pl[:48].hex()}", flush=True)
        alive = False; break
    elif pid == 0x2C and len(pl) == 8:
        ka_id = struct.unpack('>q', pl)[0]
        ka_count += 1
        # Also try responding with multiple KA IDs
        for cs_pid in cs_ka_ids:
            send_pkt(cs_pid, pl)
    elif pid == 0x79:
        try:
            msg, _ = rs(pl)
            print(f"[C] {msg[:150]}", flush=True)
        except: pass
    elif pid == 0x46:
        tid, _ = rvar(pl)
        send_pkt(0x00, wvar(tid))

print(f"\n=== {time.time()-t0:.1f}s ===")
print(f"KA received: {ka_count}", flush=True)
sock.close()
PYEOF
