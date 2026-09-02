#!/usr/bin/env python3
"""
Raw packet dump for config state - shows every packet.
"""
import socket, struct, time, uuid, zlib, threading

HOST, PORT = "skyblock.chals.sekai.team", 25565
PV = 775

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

class DumpBot:
    def __init__(self):
        self.uname = f"Bot{int(time.time())%10000}"
        self.pwd = "pw" + str(int(time.time())%10000)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None

    def send_raw(self, data):
        raw = data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw); f = wvar(len(raw)) + c
            else: f = wvar(0) + raw
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(raw)) + raw)

    def send_pkt(self, pid, data=b''):
        self.send_raw(wvar(pid) + data)

    def recv(self, timeout=15):
        self.sock.settimeout(timeout)
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

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        # LOGIN
        while True:
            pid, pl = self.recv()
            if pid is None: return
            if pid == 0x00:
                print(f"[!] Rejected: {pl[:60].hex()}", flush=True)
                return
            elif pid == 0x02:
                self.send_pkt(0x03)
                break
            elif pid == 0x03:
                self.cp, _ = rvar(pl)
                print(f"[*] Compression threshold={self.cp}", flush=True)
            elif pid == 0x04:
                m, o = rvar(pl, 1)
                c, o = rvar(pl, o)
                ch = pl[o:o+c].decode(errors='replace') if c > 0 else ''
                print(f"[LOGIN Plugin] msg={m} channel='{ch}'", flush=True)
                self.send_pkt(0x02, wvar(m) + wvar(0))

        # CONFIG
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        t_start = time.time()
        while time.time() - t_start < 8:
            try:
                pid, pl = self.recv(2)
                if pid is None: break
            except socket.timeout:
                print("[*] config timeout", flush=True)
                break
            except: break

            print(f"[CONFIG] pid=0x{pid:02X} len={len(pl)}", end='', flush=True)
            if len(pl) < 100:
                print(f" data={pl.hex()}", end='', flush=True)
            else:
                print(f" hex={pl[:40].hex()}...", end='', flush=True)
            print(flush=True)

            if pid == 0x03:
                print("[*] Finish Config!", flush=True)
                break
            elif pid == 0x04:
                self.send_pkt(0x04, pl)
            elif pid == 0x05:
                self.send_pkt(0x05, pl)
            elif pid == 0x12:
                # Plugin message - dump the raw data without assuming format
                pass
            elif pid == 0x02:
                print(f"[!] KICK", flush=True)
                break

        self.sock.close()

if __name__ == "__main__":
    DumpBot().run()
