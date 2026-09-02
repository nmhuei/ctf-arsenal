"""
Dump ALL serverbound player-state packet IDs from Paper 26.1.2
"""
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

def recvall(sock, n):
    d = b''
    while len(d) < n:
        c = sock.recv(n - len(d))
        if not c: return d
        d += c
    return d

class Dumper:
    def __init__(self):
        self.cp = -1
        self.observed = {}  # pid -> {'count': N, 'sizes': [list]}

    def read(self, sock):
        d = b''
        while True:
            b = sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        plen, _ = rvar(d)
        rest = recvall(sock, plen)
        if self.cp >= 0:
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

    def log(self, pid, pl):
        if pid not in self.observed:
            self.observed[pid] = {'count': 0, 'sizes': [], 'hex': pl[:32].hex()}
        self.observed[pid]['count'] += 1
        if len(self.observed[pid]['sizes']) < 3:
            self.observed[pid]['sizes'].append(len(pl))

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((HOST, PORT))

        uid = uuid.uuid4()
        name = "M" + str(int(time.time()) % 1000)

        # Handshake
        self._send(sock, 0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        # Login
        self._send(sock, 0x00, wstr(name) + struct.pack('>QQ', uid.int >> 64, uid.int & ((1 << 64) - 1)))

        # Login phase
        while True:
            pid, pl = self.read(sock)
            if pid is None: return
            if pid == 0x00:
                print(f"[!] Rejected at login", flush=True); return
            if pid == 0x02:
                self._send(sock, 0x03); break
            elif pid == 0x03:
                self.cp, _ = rvar(pl)
            elif pid == 0x04:
                mid, o = rvar(pl, 1)
                self._send(sock, 0x02, wvar(mid) + wvar(0))

        # Config
        self._send(sock, 0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        config_done = False
        while True:
            pid, pl = self.read(sock)
            if pid is None: return
            if pid == 0x03:
                config_done = True
                break
            elif pid == 0x04:
                self._send(sock, 0x04, pl)
            elif pid == 0x05:
                self._send(sock, 0x05, pl)
            elif pid == 0x0E:
                cnt, o = rvar(pl)
                resp = b''
                for _ in range(cnt):
                    ns, o = self.rs(pl, o)
                    n, o = self.rs(pl, o)
                    v, o = self.rs(pl, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self._send(sock, 0x07, wvar(cnt) + resp)
            elif pid == 0x12:  # AuthMe
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', 4) + b'pw00'
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', 4) + b'pw00' + b'\x00'
                self._send(sock, 0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13:
                self._send(sock, 0x09)
            elif pid == 0x02:
                print(f"[!] Config kick", flush=True); return

        # PLAY state
        self._send(sock, 0x03)
        sock.settimeout(0.5)
        print("[+] PLAY — dumping packets for 8s...", flush=True)

        t0 = time.time()
        while time.time() - t0 < 8:
            try:
                pid, pl = self.read(sock)
                if pid is None: break
                self.log(pid, pl)
            except socket.timeout:
                pass

        sock.close()
        print(f"\n=== Packet ID dump ({len(self.observed)} unique IDs) ===", flush=True)
        for pid in sorted(self.observed.keys()):
            info = self.observed[pid]
            sz_str = '/'.join(str(s) for s in info['sizes'][:3])
            print(f"  0x{pid:02x}: count={info['count']:4d} sizes={sz_str} hex={info['hex'][:40]}", flush=True)

    def _send(self, sock, pid, data=b''):
        raw = wvar(pid) + data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw)
                sock.sendall(wvar(len(wvar(len(raw))+c)) + wvar(len(raw)) + c)
            else:
                sock.sendall(wvar(len(wvar(0)+raw)) + wvar(0) + raw)
        else:
            sock.sendall(wvar(len(raw)) + raw)

    def rs(self, d, o=0):
        l, o = rvar(d, o)
        return d[o:o+l].decode(), o+l

Dumper().run()
