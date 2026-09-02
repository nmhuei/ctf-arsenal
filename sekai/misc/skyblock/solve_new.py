"""
SEKAI CTF 2026 — Skyblock Solver v2
Paper 26.1.2 protocol 775 — correct packet IDs from live traffic.
"""
import socket, struct, time, uuid, zlib, threading, re, json

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

class Client:
    def __init__(self, suffix=""):
        self.uname = f"B{int(time.time())%10000}{suffix}"
        self.pwd = f"pw{int(time.time())%10000}"
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []
        self.keep_running = True

    def send_raw(self, data):
        if self.cp >= 0:
            if len(data) >= self.cp:
                c = zlib.compress(data)
                f = wvar(len(data)) + c
            else:
                f = wvar(0) + data
            self.sock.sendall(wvar(len(f)) + f)
        else:
            self.sock.sendall(wvar(len(data)) + data)

    def send_pkt(self, pid, data=b''):
        self.send_raw(wvar(pid) + data)

    def recv_pkt(self):
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        plen, _ = rvar(d)
        rest = b''
        while len(rest) < plen:
            c = self.sock.recv(plen - len(rest))
            if not c: return None, None
            rest += c
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

    def rs(self, d, o=0):
        l, o = rvar(d, o)
        return d[o:o+l].decode(errors='replace'), o+l

    def extract_json(self, obj):
        if isinstance(obj, str): return obj
        if isinstance(obj, dict):
            parts = []
            if obj.get('text'): parts.append(obj['text'])
            if obj.get('translate'):
                args = [self.extract_json(a) for a in obj.get('with', [])]
                parts.append(f"{obj['translate']} {' '.join(args)}".strip())
            if 'extra' in obj:
                for e in obj['extra']:
                    t = self.extract_json(e)
                    if t: parts.append(t)
            return ''.join(parts)
        if isinstance(obj, list): return ''.join(self.extract_json(i) for i in obj)
        return ''

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        print(f"[*] {self.uname} connecting...", flush=True)

        # Handshake
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        # Login Start
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        while True:
            pid, pl = self.recv_pkt()
            if pid is None: return False
            if pid == 0x00:  # Disconnect
                try:
                    sl, o = rvar(pl)
                    msg = pl[o:o+sl].decode()
                    print(f"[!] Login rejected: {msg[:200]}", flush=True)
                except: pass
                return False
            elif pid == 0x02:  # Login Success
                self.send_pkt(0x03)  # Login Acknowledged
                break
            elif pid == 0x03:  # Set Compression
                self.cp, _ = rvar(pl)
            elif pid == 0x04:  # Login Plugin Request
                mid, o = rvar(pl, 1)
                self.send_pkt(0x02, wvar(mid) + wvar(0))

        # === CONFIG state ===
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        while True:
            pid, pl = self.recv_pkt()
            if pid is None: return False

            if pid == 0x03:  # finish_configuration
                break
            elif pid == 0x04:  # keep_alive (ping)
                self.send_pkt(0x04, pl)
            elif pid == 0x05:  # ping (pong)
                self.send_pkt(0x05, pl)
            elif pid == 0x0E:  # select_known_packs
                cnt, o = rvar(pl)
                resp = b''
                for _ in range(cnt):
                    ns, o = self.rs(pl, o)
                    n, o = self.rs(pl, o)
                    v, o = self.rs(pl, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send_pkt(0x07, wvar(cnt) + resp)
            elif pid == 0x12:  # show_dialog (AuthMe form)
                print(f"[FORM] AuthMe detected, registering with password: {self.pwd}", flush=True)
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x00'
                self.send_pkt(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01'+nbt)) + b'\x01'+nbt)
            elif pid == 0x13:  # code_of_conduct
                self.send_pkt(0x09)  # accept
            elif pid == 0x02:  # disconnect
                try:
                    sl, o = rvar(pl)
                    msg = pl[o:o+sl].decode()
                    print(f"[!] Config kick: {msg[:200]}", flush=True)
                except: pass
                return False

        # === PLAY state ===
        self.send_pkt(0x03)  # finish_configuration
        self.sock.settimeout(1)
        print(f"[+] PLAY state", flush=True)

        # Tick-end heartbeat
        def hb():
            while self.keep_running:
                try:
                    self.send_pkt(0x0C)  # tick_end
                    time.sleep(0.5)
                except: break
        threading.Thread(target=hb, daemon=True).start()

        return True

    def run(self, commands=None):
        if not self.connect():
            return False

        if commands is None:
            commands = ['balance', 'tradebook help', 'tradebook list']

        ci = 0
        t0 = time.time()
        loaded = False
        seen_msgs = set()

        while self.keep_running:
            now = time.time()

            try:
                pid, pl = self.recv_pkt()
                if pid is None: break
            except socket.timeout:
                pid = None
            except:
                break

            if pid is None:
                pass
            elif pid == 0x1B:  # keep_alive (long)
                self.send_pkt(0x1B, pl)
            elif pid == 0x31:  # login/join game
                if not loaded:
                    self.send_pkt(0x2B)  # player_loaded
                    self.send_pkt(0x0D, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
                    print("[*] Loaded!", flush=True)
                    # Send commands immediately
                    for cmd in commands[:3]:
                        print(f">>> /{cmd}", flush=True)
                        ts = int(time.time() * 1000)
                        self.send_pkt(0x06, wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00')
                        time.sleep(0.5)
                    ci = len(commands[:3])
            elif pid == 0x46:  # position
                tid, _ = rvar(pl)
                self.send_pkt(0x00, wvar(tid))  # teleport_confirm
            elif pid == 0x20:  # kick/disconnect
                try:
                    sl, o = rvar(pl)
                    msg = pl[o:o+sl].decode(errors='replace')
                    msg = re.sub(r'\xa7.', '', msg)
                    if msg.strip():
                        print(f"[KICK] {msg[:300]}", flush=True)
                except:
                    print(f"[KICK] raw hex: {pl[:60].hex()}", flush=True)
                break
            elif pid == 0x77:  # system_chat
                try:
                    msg, _ = self.rs(pl)
                    if msg.startswith('{'):
                        j = json.loads(msg)
                        txt = self.extract_json(j)
                    else:
                        txt = msg
                    txt = re.sub(r'\xa7.', '', txt).strip()
                    if txt and txt not in seen_msgs:
                        seen_msgs.add(txt)
                        self.msgs.append(txt)
                        print(f"[C] {txt[:500]}", flush=True)
                except:
                    pass
            elif pid == 0x6E:  # set_title_subtitle
                try:
                    ttype, o = rvar(pl)
                    msg, _ = self.rs(pl, o)
                    if msg.startswith('{'):
                        j = json.loads(msg)
                        txt = self.extract_json(j)
                    else:
                        txt = msg
                    txt = re.sub(r'\xa7.', '', txt).strip()
                    if txt and txt not in seen_msgs:
                        seen_msgs.add(txt)
                        self.msgs.append(txt)
                        print(f"[T] {txt[:300]}", flush=True)
                except: pass
            elif pid == 0x70:  # set_title_text
                try:
                    msg, _ = self.rs(pl)
                    if msg.startswith('{'):
                        j = json.loads(msg)
                        txt = self.extract_json(j)
                    else:
                        txt = msg
                    txt = re.sub(r'\xa7.', '', txt).strip()
                    if txt and txt not in seen_msgs:
                        seen_msgs.add(txt)
                        self.msgs.append(txt)
                        print(f"[T] {txt[:300]}", flush=True)
                except: pass
            elif pid == 0x55:  # action_bar
                try:
                    msg, _ = self.rs(pl)
                    if msg.startswith('{'):
                        j = json.loads(msg)
                        txt = self.extract_json(j)
                    else:
                        txt = msg
                    txt = re.sub(r'\xa7.', '', txt).strip()
                    if txt and txt not in seen_msgs:
                        seen_msgs.add(txt)
                        self.msgs.append(txt)
                        print(f"[A] {txt[:300]}", flush=True)
                except: pass
            elif pid == 0x74:  # start_configuration
                print("[*] Back to config", flush=True)
                break

            # Send remaining commands
            if ci < len(commands) and now - t0 > 3 + ci * 4:
                cmd = commands[ci]
                print(f">>> /{cmd}", flush=True)
                ts = int(time.time() * 1000)
                self.send_pkt(0x06, wstr(cmd) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + b'\x00')
                ci += 1

            if ci >= len(commands) and now - t0 > 55:
                break
            if now - t0 > 60:
                break

        self.keep_running = False
        self.sock.close()

        print(f"\n{'='*60}", flush=True)
        print(f"RESULTS ({len(self.msgs)} messages):", flush=True)
        print('='*60, flush=True)
        for m in self.msgs:
            print(f"  {m[:300]}", flush=True)

        for m in self.msgs:
            low = m.lower()
            if 'sekai' in low or 'flag' in low or 'tbctf' in low or 'ctf{' in low:
                print(f"\n*** FLAG: {m} ***", flush=True)
                return m
        return True

if __name__ == "__main__":
    import sys
    c = Client(sys.argv[1] if len(sys.argv) > 1 else '')
    c.run()
