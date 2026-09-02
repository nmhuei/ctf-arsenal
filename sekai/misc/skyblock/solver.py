"""
Minecraft Protocol Client for 26.1.2 (Protocol 775) - SEKAI CTF Skyblock
Complete solver with NBT chat parsing, /tradebook interaction,
and arbitrage detection.
"""
import socket, struct, time, uuid, zlib, json, threading, sys

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

class Solver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        ts = int(time.time() % 10000)
        self.uname = "Bot_" + str(ts)
        self.pwd = "pw_" + str(ts)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.msgs = []
        self.known_players = set()
        self.balance = 0
        self.tradebook_info = ""
        self.inventory = {}
        self.running = True

    def log(self, m): print(m, flush=True)
    def debug(self, m): print(f"  [DBG] {m}", flush=True)

    # --- Low level ---
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

    # --- NBT Parser ---
    def parse_nbt(self, data, offset=0, anonymous=False):
        """Parse NBT, return structured result"""
        try:
            if offset >= len(data): return None, offset
            tt = data[offset]; offset += 1
            if tt == 0: return None, offset
            fn = b''
            if not anonymous:
                if offset + 2 > len(data): return None, offset
                nl = struct.unpack('>H', data[offset:offset+2])[0]; offset += 2
                if nl:
                    fn = data[offset:offset+nl]; offset += nl
            if tt == 0x08:  # String
                vl = struct.unpack('>H', data[offset:offset+2])[0]; offset += 2
                v = data[offset:offset+vl]; offset += vl
                return {'type': 'str', 'name': fn, 'val': v.decode('utf-8', errors='replace')}, offset
            elif tt == 0x0a:  # Compound
                fields = {}
                while offset < len(data) and data[offset] != 0:
                    r, offset = self.parse_nbt(data, offset, False)
                    if r and r['name']: fields[r['name']] = r
                if offset < len(data) and data[offset] == 0: offset += 1
                return {'type': 'compound', 'name': fn, 'val': fields}, offset
            elif tt == 0x09:  # List
                lt = data[offset]; offset += 1
                ll = struct.unpack('>I', data[offset:offset+4])[0]; offset += 4
                items = []
                for _ in range(ll):
                    r, offset = self.parse_nbt(data, offset, True)
                    if r: items.append(r)
                return {'type': 'list', 'name': fn, 'val': items}, offset
            elif tt == 0x01:  # Byte
                return {'type': 'byte', 'name': fn, 'val': data[offset]}, offset+1
            elif tt == 0x02:  # Short
                v = struct.unpack('>h', data[offset:offset+2])[0]; offset += 2
                return {'type': 'short', 'name': fn, 'val': v}, offset
            elif tt == 0x03:  # Int
                v = struct.unpack('>i', data[offset:offset+4])[0]; offset += 4
                return {'type': 'int', 'name': fn, 'val': v}, offset
            elif tt == 0x04:  # Long
                v = struct.unpack('>q', data[offset:offset+8])[0]; offset += 8
                return {'type': 'long', 'name': fn, 'val': v}, offset
            elif tt == 0x05:  # Float
                v = struct.unpack('>f', data[offset:offset+4])[0]; offset += 4
                return {'type': 'float', 'name': fn, 'val': v}, offset
            elif tt == 0x06:  # Double
                v = struct.unpack('>d', data[offset:offset+8])[0]; offset += 8
                return {'type': 'double', 'name': fn, 'val': v}, offset
            return None, offset
        except: return None, offset

    def nbt_to_text(self, node):
        """Extract plain text from an NBT chat component node"""
        if node is None: return ''
        t = node['type']
        if t == 'str':
            n = node['name']
            if n in (b'text', b'translate', b''):
                return node['val']
            return ''
        elif t == 'compound':
            v = node['val']
            # Check for 'text' or 'translate' field
            text = ''
            if b'text' in v:
                text += self.nbt_to_text(v[b'text'])
            if b'translate' in v:
                text += self.nbt_to_text(v[b'translate'])
            if b'with' in v:
                with_list = v[b'with']
                if with_list['type'] == 'list':
                    for item in with_list['val']:
                        text += self.nbt_to_text(item)
            if b'extra' in v:
                extra = v[b'extra']
                if extra['type'] == 'list':
                    for item in extra['val']:
                        text += self.nbt_to_text(item)
            return text
        elif t == 'list':
            return ''.join(self.nbt_to_text(item) for item in node['val'])
        return ''

    def parse_chat(self, data, offset=0):
        """Parse NBT chat and return plain text"""
        node, _ = self.parse_nbt(data, offset, True)
        if node:
            return self.nbt_to_text(node).strip()
        return ''

    # --- Chat command ---
    def send_cmd(self, cmd):
        """Send a chat command like /tradebook"""
        self.log(f">>> /{cmd}")
        # Chat Commands (0x07) for protocol 775:
        # command (String), timestamp (Long), salt (Long),
        # argumentSignatures (VarInt count), messageCount (VarInt), acknowledged (BitSet)
        msg = wstr(cmd)  # command without leading /
        msg += struct.pack('>q', int(time.time() * 1000))  # timestamp
        msg += struct.pack('>q', 0)  # salt
        msg += wvar(0)  # argumentSignatures count
        msg += wvar(0)  # messageCount
        msg += b'\x00'  # acknowledged BitSet
        self.send(0x07, msg)

    def send_chat_msg(self, text):
        """Send a chat message"""
        msg = wstr(text)
        timestamp = int(time.time() * 1000)
        msg += struct.pack('>q', timestamp)
        msg += struct.pack('>q', 0)  # salt
        msg += b'\x01' + wstr(self.uid.hex)  # signature
        msg += b'\x01'  # messageCount (1)
        # Previous messages: for this, just empty
        msg += wvar(0)  # acknowledged range count
        msg += b'\x00'  # acknowledged bitset
        self.send(0x09, msg)

    def send_client_info(self):
        info = wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0])
        self.send(0x00, info)

    # --- Main loop ---
    def run(self):
        self.log(f"Connecting to {HOST}:{PORT}...")
        self.sock.connect((HOST, PORT))
        self.log(f"Connected as {self.uname} / {self.uid}")

        # Handshake -> LOGIN
        hs = wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2)
        self.send(0x00, hs)
        self.send(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        # LOGIN state
        self.log("\n--- LOGIN ---")
        while True:
            pid, pl = self.recv()
            if pid == 0x02:
                u, _ = self.rs(pl, 16)
                self.log(f"Login: {u}")
                self.send(0x03)  # Ack -> CONFIG
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

        # CONFIG state
        self.log("\n--- CONFIG ---")
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            pid, pl = self.recv()
            if pid == 0x01:
                c, o = self.rs(pl); d = pl[o:]
                if c == "minecraft:brand":
                    bl, bo = rvar(d); self.log(f"Brand: {d[bo:bo+bl].decode()}")
                else:
                    self.debug(f"Plugin: {c}")
            elif pid == 0x03: break  # Finish config
            elif pid == 0x04: self.send(0x04, pl)
            elif pid == 0x05: self.send(0x05, pl)
            elif pid == 0x07: pass
            elif pid == 0x0C: pass
            elif pid == 0x0D: pass
            elif pid == 0x0E:
                self.send(0x07, wvar(0))
            elif pid == 0x11: pass
            elif pid == 0x12:  # AuthMe dialog
                nbt_pwd = b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt_cfm = b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt = b'\x0a\x00\x00' + nbt_pwd + nbt_cfm + b'\x00'
                opt = b'\x01' + nbt
                click = wstr("authme:prejoin-register/submit") + wvar(len(opt)) + opt
                self.send(0x08, click)
                self.log(f"Registered: {self.pwd}")
            elif pid == 0x13:
                self.send(0x09)
                self.log("Accepted code of conduct")
            else:
                self.debug(f"Config pkt 0x{pid:02X}")

        # PLAY state
        self.send(0x03)
        self.log("\n--- PLAY ---")
        self.sock.settimeout(10)

        # Start keepalive thread
        def hb():
            while self.running:
                time.sleep(0.5)
                self.send(0x24, b'\x00' * 8)  # Tick End
        t = threading.Thread(target=hb, daemon=True)
        t.start()

        # Main play loop
        self.play_loop()

    def play_loop(self):
        cmds = [
            "/balance",
            "/tradebook help",
            "/tradebook list",
            "/tradebook",
        ]
        ci = 0
        t0 = time.time()
        player_loaded = False
        sent_commands = set()

        while self.running:
            try: pid, pl = self.recv()
            except (socket.timeout, ConnectionError): break
            except: break

            if pid == 0x2C:  # Keep Alive
                self.send(0x1C, pl)
            elif pid == 0x31:  # Login/Join
                if not player_loaded:
                    self.send(0x2C)  # Player Loaded
                    self.send_client_info()
                    player_loaded = True
            elif pid == 0x48:  # Position
                self.send(0x00, wvar(0))
            elif pid == 0x20:  # Disconnect
                try:
                    txt = self.parse_chat(pl)
                    self.log(f"[KICK] {txt}")
                except: self.log(f"[KICK] raw={pl[:60].hex()}")
                break
            elif pid == 0x79:  # System Chat
                # Parse NBT chat component
                txt = self.parse_chat(pl)
                if txt:
                    self.log(f"[CHAT] {txt}")
                    self.msgs.append(txt)
                    self.analyze_chat(txt)
                else:
                    self.debug(f"Empty chat, raw={pl[:40].hex()}")
            elif pid == 0x0E:  # Open Screen
                self.log("[OPEN SCREEN]")
            elif pid == 0x3B:  # Open Screen
                self.log("[OPEN SCREEN]")
            elif pid == 0x18:  # Custom Payload
                try:
                    ch, o = self.rs(pl)
                    self.debug(f"Plugin: {ch}")
                except: pass
            elif pid == 0x76:  # Start Config
                self.log("[START CONFIG] re-entering config")
                break
            elif pid == 0x6E:  # Action bar / Title
                try:
                    txt = self.parse_chat(pl)
                    if txt: self.log(f"[TITLE] {txt}")
                except: pass
            elif pid not in (0x2D, 0x30, 0x5E, 0x5F, 0x68, 0x0B, 0x0C, 0x65, 0x35,
                             0x00, 0x01, 0x02, 0x3D, 0x38, 0x7C, 0x83, 0x75,
                             0x54, 0x2F, 0x05, 0x66, 0x71, 0x7A, 0x19, 0x46,
                             0x45, 0x41, 0x61, 0x56, 0x20, 0x5B, 0x22, 0x4A,
                             0x5C, 0x59, 0x5A, 0x58, 0x69, 0x6F, 0x70, 0x73,
                             0x74, 0x76, 0x77, 0x78, 0x81, 0x82, 0x84, 0x85,
                             0x86, 0x87, 0x88, 0x89, 0x8B, 0x8A, 0x16, 0x64,
                             0x4D, 0x53, 0x63, 0x67, 0x72, 0x6C, 0x6D, 0x4F,
                             0x4E, 0x4B, 0x4C, 0x6B, 0x60, 0x62, 0x8C, 0x6A):
                try:
                    txt = pl[:40].decode('utf-8', errors='replace')
                    self.debug(f"PKT 0x{pid:02X}: {txt!r}")
                except: pass

            # Send commands progressively
            if ci < len(cmds) and time.time() - t0 > 3 + ci * 5:
                self.send_cmd(cmds[ci])
                ci += 1

        self.log(f"\n=== Summary: {len(self.msgs)} messages ===")
        for m in self.msgs:
            self.log(f"  {m[:200]}")

    def analyze_chat(self, txt):
        """Analyze chat messages for useful info"""
        txt_lower = txt.lower()
        if 'balance' in txt_lower or 'coins' in txt_lower or '$' in txt:
            # Try to extract number
            import re
            nums = re.findall(r'[\d,]+', txt.replace(',', ''))
            for n in nums:
                try: self.balance = int(n.replace(',', ''))
                except: pass
            self.log(f"  => Balance: {self.balance}")
        if 'tradebook' in txt_lower:
            self.tradebook_info += txt + "\n"

    def close(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except: pass

if __name__ == "__main__":
    s = Solver()
    try: s.run()
    except Exception as e:
        print(f"\nError: {e}", flush=True)
        import traceback; traceback.print_exc()
    finally:
        s.close()
        print("\nDone", flush=True)
