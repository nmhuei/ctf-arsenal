"""
Minecraft Client v10 - minimal, test /tradebook command with debug
"""
import socket, struct, time, uuid, zlib

HOST = "skyblock.chals.sekai.team"
PORT = 25565
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

def wstr(s): e = s.encode('utf-8'); return wvar(len(e)) + e
def wu64(v): return struct.pack('>Q', v)

class Bot:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.uname = "Bot_" + str(int(time.time() % 100000))
        self.uid = uuid.uuid4()
        self.cp = -1
        self.msg = []
        self.known = set()

    def connect(self):
        self.sock.connect((HOST, PORT))
        self.log(f"Connected as {self.uname} / {self.uid}")

    def log(self, m): print(m, flush=True)

    def send(self, pid, data=b''):
        raw = wvar(pid) + data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw); f = wvar(len(raw)) + c
            else: f = wvar(0) + raw
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(raw)) + raw)

    def recv(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: raise ConnectionError("Closed")
            d += b
            if not (b[0] & 0x80): break
        l, _ = rvar(d)
        rest = b''
        while len(rest) < l:
            c = self.sock.recv(l - len(rest))
            if not c: raise ConnectionError("Closed")
            rest += c
        if self.cp >= 0:
            dl, o = rvar(rest)
            if dl > 0:
                dec = zlib.decompress(rest[o:])
                pid, o2 = rvar(dec); return pid, dec[o2:]
            else: pid, o2 = rvar(rest, o); return pid, rest[o2:]
        else: pid, o = rvar(rest); return pid, rest[o:]

    def rs(self, d, o=0):
        l, o = rvar(d, o); return d[o:o+l].decode('utf-8'), o+l

    def run(self):
        self.connect()
        # Handshake
        hs = wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2)
        self.send(0x00, hs)
        # Login Start
        self.send(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))
        # Wait for login
        self.log("\n--- LOGIN ---")
        while True:
            pid, pl = self.recv()
            if pid == 0x02:
                u, _ = self.rs(pl, 16)
                self.log(f"Login: {u}")
                self.send(0x03)  # Login Ack -> CONFIG
                break
            elif pid == 0x03:
                self.cp, _ = rvar(pl)
                self.log(f"Compression: {self.cp}")
            elif pid == 0x04:
                m, o = rvar(pl); c, o = self.rs(pl, o)
                self.log(f"Plugin: {c}")
                self.send(0x02, wvar(m) + wvar(0))
            elif pid == 0x00:
                r, _ = self.rs(pl)
                self.log(f"Disconnect: {r}"); return
        # CONFIG
        self.log("\n--- CONFIG ---")
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        cf = False
        while not cf:
            pid, pl = self.recv()
            if pid == 0x01:
                c, o = self.rs(pl); d = pl[o:]
                if c == "minecraft:brand":
                    bl, bo = rvar(d); self.log(f"Brand: {d[bo:bo+bl].decode()}")
            elif pid == 0x03: cf = True
            elif pid == 0x04: self.send(0x04, pl)
            elif pid == 0x05: self.send(0x05, pl)
            elif pid == 0x0d: pass
            elif pid == 0x0c: pass
            elif pid == 0x07: pass
            elif pid == 0x0e:
                self.send(0x07, wvar(0))
            elif pid == 0x11: pass
            elif pid == 0x12:
                # AuthMe
                pwd = "pw_" + self.uname[4:]
                def wnbt(name, val):
                    nb = name.encode(); vb = val.encode()
                    return b'\x08' + struct.pack('>H', len(nb)) + nb + struct.pack('>H', len(vb)) + vb
                nbt = b'\x0a\x00\x00' + wnbt("password", pwd) + wnbt("confirm", pwd) + b'\x00'
                opt = b'\x01' + nbt
                click = wstr("authme:prejoin-register/submit") + wvar(len(opt)) + opt
                self.send(0x08, click)
                self.log(f"Registered: {pwd}")
            elif pid == 0x13:
                self.send(0x09)
                self.log("Accepted code of conduct")
        # Send finish config
        self.send(0x03)
        self.log("\n--- PLAY ---")
        self.sock.settimeout(8)
        # Wait for spawn
        cmds = ["/tradebook", "/tradebook list", "/balance", "/tradebook help"]
        ci = 0
        t0 = time.time()
        while True:
            try: pid, pl = self.recv()
            except (socket.timeout, ConnectionError): break
            # Handle packets
            if pid == 0x2c:  # Keep Alive
                self.send(0x1c, pl)
            elif pid == 0x31:  # Login/Join
                self.send(0x2c)  # Player Loaded
                self.send(0x0e, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
            elif pid == 0x48:  # Position
                self.send(0x00, wvar(0))
            elif pid == 0x79:  # System Chat
                self.log(f"  [CHAT RAW] hex={pl[:80].hex()}")
                self.parse_nbt_chat(pl)
            elif pid == 0x6E:  # Action bar / set title
                pass
            elif pid == 0x0E:  # Open Screen (container)
                self.log("  [OPEN SCREEN]")
            elif pid not in (0x2D, 0x30, 0x5E, 0x5F, 0x68, 0x0B, 0x0C, 0x65, 0x35, 0x8A, 0x23, 0x63, 0x53, 0x36, 0x00, 0x01, 0x08, 0x02, 0x3D, 0x38, 0x7C, 0x83, 0x75, 0x54, 0x2F, 0x05, 0x66, 0x71, 0x7A, 0x19, 0x46, 0x45, 0x41, 0x61, 0x56, 0x20, 0x5B, 0x22, 0x4A, 0x5C, 0x59, 0x5A, 0x58, 0x69, 0x6F, 0x70, 0x73, 0x74, 0x76, 0x77, 0x78, 0x81, 0x82, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8B):
                # Unknown - show first few bytes
                try:
                    txt = pl[:60].decode('utf-8', errors='replace')
                    self.log(f"  [PKT {pid}] hex={pl[:40].hex()} str={txt!r}")
                except:
                    self.log(f"  [PKT {pid}] hex={pl[:40].hex()}")
            # Send commands
            if ci < len(cmds) and time.time() - t0 > 3 + ci * 4:
                cmd = cmds[ci]
                self.log(f"\n>>> / {cmd}")
                self.send(0x07, wstr(cmd[1:]))
                ci += 1

    def parse_nbt_chat(self, data, o=0, anon=False):
        try:
            if o >= len(data): return '', o
            tt = data[o]; o += 1
            if tt == 0: return '', o
            fn = ''
            if not anon:
                nl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                if nl: fn = data[o:o+nl].decode('utf-8', errors='replace'); o += nl
            if tt == 0x08:  # String
                vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                if o + vl > len(data): vl = len(data) - o
                t = data[o:o+vl].decode('utf-8', errors='replace'); o += vl
                if fn in ('text', 'translate', '') and t.strip():
                    self.log(f"  [CHAT] {t[:300]}")
                    self.msg.append(t)
                return '', o
            elif tt == 0x0a:  # Compound
                while o < len(data):
                    if data[o] == 0: o += 1; break
                    ft, o = self.parse_nbt_chat(data, o, False)
            elif tt == 0x09:  # List
                lt = data[o]; o += 1
                ll = struct.unpack('>I', data[o:o+4])[0]; o += 4
                for _ in range(ll):
                    ft, o = self.parse_nbt_chat(data, o, True)
            return '', o
        except Exception as e:
            self.log(f"  [NBT ERR] {e}")
            return '', o

    def close(self):
        if self.sock: self.sock.close()

if __name__ == "__main__":
    b = Bot()
    try: b.run()
    except Exception as e: print(f"Error: {e}", flush=True); import traceback; traceback.print_exc()
    finally:
        print(f"\n=== Messages ({len(b.msg)}) ===")
        for m in b.msg: print(f"  {m[:200]}")
        b.close()
