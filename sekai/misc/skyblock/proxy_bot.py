#!/usr/bin/env python3
"""
Skyblock Proxy Rotator Bot
Rotates SOCKS5 proxies to bypass AntiBot IP block.
Connects, registers, stays alive, captures server data.
"""
import socket, struct, time, uuid, zlib, sys, threading, json, urllib.request
import socks  # PySocks

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

def fetch_proxies():
    """Fetch live SOCKS5 proxies from public sources"""
    proxies = []
    sources = [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=5000&country=all&ssl=all&anonymity=all',
    ]
    for url in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            data = resp.read().decode().strip()
            for line in data.splitlines():
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    proxies.append(line)
        except Exception as e:
            print(f"[!] Proxy source failed: {e}", flush=True)
    # Remove duplicates, keep order
    seen = set()
    unique = []
    for p in proxies:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    print(f"[+] Fetched {len(unique)} SOCKS5 proxies", flush=True)
    return unique

def test_proxy(proxy_str, timeout=8):
    """Test if proxy can reach skyblock server"""
    host, port_str = proxy_str.split(':')
    port = int(port_str)
    try:
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, host, port)
        s.settimeout(timeout)
        s.connect((HOST, PORT))
        s.close()
        return True
    except Exception as e:
        return False

class ProxyBot:
    def __init__(self, proxy_str=None):
        self.cp = -1
        self.uid = uuid.uuid4()
        ts = int(time.time())
        self.name = f"R{ts%10000}"
        self.pwd = f"pw{ts%10000}"
        self.sock = None
        self.msgs = []
        self.proxy = proxy_str
        self.alive = False

    def _make_socket(self):
        if self.proxy:
            host, port_str = self.proxy.split(':')
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS5, host, int(port_str))
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        return s

    def send(self, pid, data=b''):
        r = wvar(pid) + data
        if self.cp >= 0:
            if len(r) >= self.cp:
                c = zlib.compress(r); f = wvar(len(r)) + c
            else: f = wvar(0) + r
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(r)) + r)

    def recv(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        pl, _ = rvar(d)
        rt = b''
        while len(rt) < pl:
            c = self.sock.recv(pl - len(rt))
            if not c: return None, None
            rt += c
        if self.cp >= 0:
            dl, o = rvar(rt)
            if dl > 0:
                dec = zlib.decompress(rt[o:])
                p, o2 = rvar(dec); return p, dec[o2:]
            else: p, o2 = rvar(rt, o); return p, rt[o2:]
        else: p, o = rvar(rt); return p, rt[o:]

    def connect(self):
        """Login + config + AuthMe registration"""
        self.sock = self._make_socket()
        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            self.sock.close()
            return False, f"CONNECT_FAIL:{e}"

        # Handshake + Login
        self.send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send(0x00, wstr(self.name) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))
        while True:
            p, pl = self.recv()
            if p is None: return False, "DISCONNECT"
            if p == 0x00:
                l, o = rvar(pl); msg = pl[o:o + l].decode(errors='replace')
                return False, f"ANTIBOT:{msg[:40]}"
            if p == 0x02: self.send(0x03); break
            elif p == 0x03: self.cp, _ = rvar(pl)
            elif p == 0x04:
                m, o = rvar(pl, 1); self.send(0x02, wvar(m) + wvar(0))

        # Config state — client settings
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            p, pl = self.recv()
            if p is None: return False, "CONFIG_DISC"
            if p == 0x03: break
            elif p == 0x04: self.send(0x04, pl)
            elif p == 0x05: self.send(0x05, pl)
            elif p == 0x0E:
                cnt, o = rvar(pl); resp = b''
                for _ in range(cnt):
                    l, o = rvar(pl, o); ns = pl[o:o + l].decode(); o += l
                    l, o = rvar(pl, o); n = pl[o:o + l].decode(); o += l
                    l, o = rvar(pl, o); v = pl[o:o + l].decode(); o += l
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send(0x07, wvar(cnt) + resp)
            elif p == 0x12:
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01' + nbt)) + b'\x01' + nbt)
            elif p == 0x13: self.send(0x09)
            elif p == 0x02:
                l, o = rvar(pl); return False, f"CFGKICK:{pl[o:o + l].decode(errors='replace')[:40]}"

        # Enter PLAY
        self.send(0x03)
        return True, "OK"

    def parse_chat(self, pl):
        if not pl: return ""
        def _scan(d, off):
            r = []
            while off < len(d):
                tt = d[off]
                if tt == 0: return "".join(r), off + 1
                off += 1
                if off + 2 > len(d): break
                nl = struct.unpack('>H', d[off:off + 2])[0]
                nm = d[off + 2:off + 2 + nl].decode(errors='replace') if nl else ''
                off += 2 + nl
                if tt == 0x08:
                    if off + 2 > len(d): break
                    sl = struct.unpack('>H', d[off:off + 2])[0]
                    if off + sl + 2 > len(d): break
                    val = d[off + 2:off + 2 + sl].decode(errors='replace'); off += 2 + sl
                    if nm in ('text', ''): r.append(val)
                elif tt == 0x09:
                    if off + 5 > len(d): break
                    lt, ll = d[off], struct.unpack('>I', d[off + 1:off + 5])[0]; off += 5
                    for _ in range(ll):
                        if lt == 0x0a: s, off = _scan(d, off); r.append(s)
                        elif lt == 0x08:
                            if off + 2 > len(d): break
                            sl = struct.unpack('>H', d[off:off + 2])[0]
                            r.append(d[off + 2:off + 2 + sl].decode(errors='replace')); off += 2 + sl
                        else: break
                elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
                else: break
            return "".join(r), off
        try:
            result, _ = _scan(pl, 1)
            return result.replace('\xa7', '').strip()
        except: return ""

    def listen(self, timeout=20):
        """Stay connected, capture all data"""
        self.sock.settimeout(0.5)
        t0 = time.time()
        loaded = False

        while time.time() - t0 < timeout:
            try:
                p, pl = self.recv()
                if p is None: break
            except socket.timeout: continue
            except: break

            if p == 0x31 and not loaded:
                self.send(0x2C)
                self.send(0x0E, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                loaded = True
                self.alive = True
                print(f"  [+] PLAY ready @{time.time()-t0:.1f}s", flush=True)

            elif p == 0x79:
                txt = self.parse_chat(pl)
                if txt and txt not in self.msgs:
                    self.msgs.append(txt)
                    print(f"  [C] {txt[:150]}", flush=True)

            elif p == 0x20:
                l, o = rvar(pl, 0); m = pl[o:o + l].decode(errors='replace')
                print(f"  [!] KICK @{time.time()-t0:.1f}s: {m[:40]}", flush=True)
                return False

            elif p == 0x46 and len(pl) < 50:
                tid, _ = rvar(pl); self.send(0x00, wvar(tid))

        self.alive = True
        return True

    def close(self):
        try: self.sock.close()
        except: pass


def test_proxies_fast(proxies, limit=50):
    """Quick connectivity test, return first working batch"""
    working = []
    tested = 0
    for p in proxies:
        if tested >= limit: break
        tested += 1
        if test_proxy(p):
            working.append(p)
            print(f"  [+] Proxy OK: {p}", flush=True)
    return working


if __name__ == "__main__":
    print(f"[*] Skyblock Proxy Rotator Bot", flush=True)
    print(f"[*] Target: {HOST}:{PORT}", flush=True)

    # Fetch proxies
    print("[*] Fetching SOCKS5 proxies...", flush=True)
    all_proxies = fetch_proxies()
    if not all_proxies:
        print("[!] No proxies found! Falling back to direct connection.", flush=True)
        all_proxies = [None]

    while True:
        # Test a batch of proxies
        batch = all_proxies[:30]
        all_proxies = all_proxies[30:] + all_proxies[:30]  # rotate

        working = []
        for p in batch:
            if p is None or test_proxy(p, timeout=5):
                working.append(p)

        if not working:
            print("[!] No working proxies in batch, retrying in 30s...", flush=True)
            time.sleep(30)
            continue

        # Try each working proxy
        for proxy in working:
            bot = ProxyBot(proxy)
            ok, status = bot.connect()
            if not ok:
                print(f"  [-] {proxy}: {status[:50]}", flush=True)
                bot.close()
                time.sleep(2)
                continue

            # Connected!
            alive_s = 0
            try:
                print(f"\n[+] CONNECTED via {proxy}", flush=True)
                bot.listen(25)
                alive_s = 25
            except:
                pass
            finally:
                bot.close()

            # Check for flag
            all_text = " ".join(bot.msgs)
            for kw in ['sekai', 'flag{', 'sKey', 'tbctf', 'ctf{', 'SEKAI']:
                if kw in all_text.lower():
                    print(f"\n*** FLAG FOUND: {all_text} ***", flush=True)
                    sys.exit(0)

            print(f"  [-] No flag, trying next proxy...", flush=True)
            time.sleep(3)

        # Refresh proxy list
        print("[*] Refreshing proxy list...", flush=True)
        all_proxies = fetch_proxies() or all_proxies
        time.sleep(5)
