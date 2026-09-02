#!/usr/bin/env python3
"""
Corrected bot for SEKAICTF Minecraft Skyblock (protocol 775).
Uses correct packet IDs from minecraft-data protocol.json.
"""
import socket, struct, time, uuid, zlib, threading, re, json

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

class Bot:
    def __init__(self, suffix=""):
        self.uname = f"B{int(time.time())%10000}{suffix}"
        self.pwd = "pw" + str(int(time.time())%10000)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []

    def send_raw(self, data):
        if self.cp >= 0:
            if len(data) >= self.cp:
                c = zlib.compress(data); f = wvar(len(data)) + c
            else: f = wvar(0) + data
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(data)) + data)

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
        pl, _ = rvar(d)
        rest = b''
        while len(rest) < pl:
            c = self.sock.recv(pl - len(rest))
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

    def rlong(self, d, o=0):
        return struct.unpack('>q', d[o:o+8])[0], o+8

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))
        # Handshake
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        # Login Start
        self.send_pkt(0x00, wstr(self.uname) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))
        # Login state
        while True:
            pid, pl = self.recv()
            if pid is None: return False
            if pid == 0x00:  # Disconnect
                msg, _ = self.rs(pl)
                print(f"[!] Login rejected: {msg[:100]}", flush=True)
                return False
            elif pid == 0x02:  # Login Success
                self.send_pkt(0x03)  # Login Acknowledged
                break
            elif pid == 0x03:  # Compression
                self.cp, _ = rvar(pl)
            elif pid == 0x04:  # Login Plugin Request
                mid, o = rvar(pl, 1)
                self.send_pkt(0x02, wvar(mid) + wvar(0))

        # === CONFIG state ===
        # Send client settings
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        while True:
            pid, pl = self.recv(5)
            if pid is None:
                print("[!] Config timeout", flush=True)
                return False

            if pid == 0x03:  # finish_configuration
                break
            elif pid == 0x04:  # keep_alive
                self.send_pkt(0x04, pl)
            elif pid == 0x05:  # ping
                self.send_pkt(0x05, pl)
            elif pid == 0x0e:  # select_known_packs
                # Respond with same format (acknowledge known packs)
                cnt, o = rvar(pl)
                resp = b''
                for _ in range(cnt):
                    ns, o = self.rs(pl, o)
                    n, o = self.rs(pl, o)
                    v, o = self.rs(pl, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send_pkt(0x07, wvar(cnt) + resp)
            elif pid == 0x01:  # custom_payload
                pass  # ignore plugin messages in config
            elif pid in (0x0c, 0x0d):  # feature_flags, tags
                pass
            elif pid == 0x02:  # disconnect
                msg, _ = self.rs(pl)
                print(f"[!] Config kick: {msg[:200]}", flush=True)
                return False
            elif pid == 0x12:  # show_dialog - Form/Auth
                print(f"[FORM] len={len(pl)}", flush=True)
            elif pid == 0x13:  # code_of_conduct
                self.send_pkt(0x09)  # accept_code_of_conduct
            elif pid == 0x00:  # cookie_request
                pass  # ignore for now

        # === PLAY state ===
        self.send_pkt(0x03)  # finish_configuration
        self.sock.settimeout(1)
        print(f"[+] {self.uname}: PLAY state", flush=True)

        # Send tick_end on a background thread
        running = True
        def hb():
            while running:
                try: self.send_pkt(0x0c)  # tick_end
                except: break
                time.sleep(0.5)
        threading.Thread(target=hb, daemon=True).start()

        return True

    def chat_cmd(self, cmd):
        """Send unsigned chat command (protocol 775 0x06)."""
        # 0x06 chat_command: just the command string (no /)
        self.send_pkt(0x06, wstr(cmd))

    def send_chat_msg(self, msg):
        """Send chat message (protocol 775 0x08)."""
        ts = int(time.time() * 1000)
        # 0x08 chat_message: message, timestamp, salt, signature (optional), offset, acknowledged
        self.send_pkt(0x08, wstr(msg) + struct.pack('>q', ts) + struct.pack('>q', 0) + wvar(0) + wvar(0) + bytes(3))

    def run(self, commands=None):
        if not self.connect():
            return False

        if commands is None:
            commands = ['help', 'balance', 'tradebook help', 'tradebook list', 'shop']

        ci = 0
        t0 = time.time()
        loaded = False

        while True:
            now = time.time()
            try:
                pid, pl = self.recv(1)
                if pid is None: break
            except socket.timeout:
                pid = None
            except: break

            if pid is None:
                pass
            elif pid == 0x2b:  # keep_alive (i64)
                self.send_pkt(0x1b, pl)
            elif pid == 0x30:  # login
                if not loaded:
                    self.send_pkt(0x2b)  # player_loaded
                    self.send_pkt(0x0d, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
            elif pid == 0x46:  # position
                tid, _ = rvar(pl)  # teleport id is first varint
                self.send_pkt(0x00, wvar(tid))  # teleport_confirm
            elif pid == 0x20:  # kick_disconnect
                try:
                    from chat_parser import parse_nbt as pnbt, chat_text as ctext
                    node, _ = pnbt(pl, 0, True)
                    txt = ctext(node).strip() if node else ''
                    if txt:
                        txt = re.sub(r'\xa7.', '', txt)
                        print(f"[KICK] {txt[:300]}", flush=True)
                    else: print(f"[KICK] hex={pl[:60].hex()}", flush=True)
                except: print(f"[KICK] hex={pl[:60].hex()}", flush=True)
                break
            elif pid == 0x77:  # system_chat
                try:
                    msg, _ = self.rs(pl)
                    # Remove JSON formatting
                    if msg.startswith('{'):
                        try:
                            j = json.loads(msg)
                            txt = self._extract_json(j)
                        except: txt = msg
                    else:
                        txt = msg
                    txt = re.sub(r'\xa7.', '', txt)
                    if txt.strip():
                        self.msgs.append(txt.strip())
                        print(f"[C] {txt.strip()[:500]}", flush=True)
                except: pass
            elif pid == 0x3f:  # player_chat
                try:
                    o = 0
                    gi, o = rvar(pl, o)
                    o += 16  # skip sender UUID
                    idx, o = rvar(pl, o) if o < len(pl) else (0, o)
                    sig_f = pl[o] if o < len(pl) else 0; o += 1
                    if sig_f and o < len(pl):
                        sl, o = rvar(pl, o)
                        hlen, o = rvar(pl, o) if o < len(pl) else (0, o)
                        o += hlen + 32
                    msg, _ = self.rs(pl, o) if o < len(pl) else ('', o)
                    if msg:
                        msg = re.sub(r'\xa7.', '', msg)
                        self.msgs.append(msg)
                        print(f"[P] {msg[:300]}", flush=True)
                except: pass
            elif pid == 0x6e:  # set_title_subtitle
                try:
                    ttype, o = rvar(pl)
                    msg, _ = self.rs(pl, o) if o < len(pl) else ('', o)
                    if msg.startswith('{'):
                        try:
                            j = json.loads(msg)
                            txt = self._extract_json(j)
                        except: txt = msg
                    else: txt = msg
                    txt = re.sub(r'\xa7.', '', txt)
                    if txt.strip():
                        self.msgs.append(txt.strip())
                        print(f"[T] {txt.strip()[:300]}", flush=True)
                except: pass
            elif pid == 0x70:  # set_title_text
                try:
                    msg, _ = self.rs(pl)
                    if msg.startswith('{'):
                        try:
                            j = json.loads(msg)
                            txt = self._extract_json(j)
                        except: txt = msg
                    else: txt = msg
                    txt = re.sub(r'\xa7.', '', txt)
                    if txt.strip():
                        self.msgs.append(txt.strip())
                        print(f"[T] {txt.strip()[:300]}", flush=True)
                except: pass
            elif pid == 0x55:  # action_bar
                try:
                    msg, _ = self.rs(pl)
                    if msg.startswith('{'):
                        try:
                            j = json.loads(msg)
                            txt = self._extract_json(j)
                        except: txt = msg
                    else: txt = msg
                    txt = re.sub(r'\xa7.', '', txt)
                    if txt.strip():
                        self.msgs.append(txt.strip())
                        print(f"[A] {txt.strip()[:300]}", flush=True)
                except: pass
            elif pid == 0x74:  # start_configuration
                print("[*] Back to config", flush=True)
                break
            elif pid == 0x18:  # custom_payload (plugin message)
                pass
            elif pid in (0x08, 0x0c, 0x0a):  # block change, chunk, etc
                pass

            # Send commands
            if ci < len(commands) and now - t0 > 3 + ci * 4:
                cmd = commands[ci]
                print(f">>> /{cmd}", flush=True)
                self.chat_cmd(cmd)
                ci += 1

            if ci >= len(commands) and now - t0 > 50:
                break
            if now - t0 > 55:
                break

        self.sock.close()

        # Print results
        print(f"\n{'='*60}", flush=True)
        print(f"RESULTS ({len(self.msgs)} messages):", flush=True)
        print('='*60, flush=True)
        for m in self.msgs:
            print(f"  {m}", flush=True)

        return True

    def _extract_json(self, obj):
        if isinstance(obj, str): return obj
        if isinstance(obj, dict):
            parts = []
            if 'text' in obj: parts.append(str(obj['text']))
            if 'extra' in obj:
                for e in obj['extra']: parts.append(self._extract_json(e))
            if 'translate' in obj: parts.append(str(obj.get('with', '')))
            return ''.join(parts)
        return str(obj)

if __name__ == "__main__":
    import sys
    suffix = sys.argv[1] if len(sys.argv) > 1 else ''
    b = Bot(suffix)

    cmds = [
        'help', 'balance', 'tradebook help', 'tradebook list',
        'shop', 'leaderboard', 'baltop',
    ]

    b.run(cmds)
