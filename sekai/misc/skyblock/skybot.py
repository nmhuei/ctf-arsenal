#!/usr/bin/env python3
"""
Minecraft 26.1.2 (Protocol 775) - Corrected client for SEKAICTF Skyblock.
Handles Formkit AuthMe registration dialog properly.
"""
import socket, struct, time, uuid, zlib, threading, json, re

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
def rs(d, o=0): l, o = rvar(d, o); return d[o:o+l].decode(errors='replace'), o+l

class SkyBot:
    def __init__(self, suffix=""):
        self.uname = f"B{int(time.time())%10000}{suffix}"
        self.pwd = "pw" + str(int(time.time())%10000)
        self.uid = uuid.uuid4()
        self.cp = -1
        self.sock = None
        self.msgs = []

    def send_pkt(self, pid, data=b''):
        raw = wvar(pid) + data
        if self.cp >= 0:
            if len(raw) >= self.cp:
                c = zlib.compress(raw); out = wvar(len(raw)) + c
            else: out = wvar(0) + raw
            self.sock.sendall(wvar(len(out)) + out)
        else:
            self.sock.sendall(wvar(len(raw)) + raw)

    def recv_pkt(self, timeout=15):
        self.sock.settimeout(timeout)
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, b''
            d += b
            if not (b[0] & 0x80): break
        plen, _ = rvar(d)
        rest = b''
        while len(rest) < plen:
            c = self.sock.recv(plen - len(rest))
            if not c: return None, b''
            rest += c
        if self.cp >= 0:
            ul, o = rvar(rest)
            if ul > 0: dec = zlib.decompress(rest[o:])
            else: dec = rest[o:]
            pid, o = rvar(dec); return pid, dec[o:]
        else:
            pid, o = rvar(rest); return pid, rest[o:]

    def run(self, commands=None):
        if commands is None:
            commands = ['help', 'balance', 'tradebook help', 'tradebook list', 'shop', 'leaderboard', 'baltop']

        # Connect
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        # Handshake
        self.send_pkt(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))

        # Login Start
        uid_bytes = self.uid.bytes
        self.send_pkt(0x00, wstr(self.uname) + uid_bytes)
        print(f"[*] {self.uname}: logging in...", flush=True)

        # === LOGIN state ===
        while True:
            pid, data = self.recv_pkt()
            if pid is None: return False
            if pid == 0x00:
                msg, _ = rs(data)
                print(f"[!] Login rejected: {msg[:100]}", flush=True)
                return False
            elif pid == 0x02:
                self.send_pkt(0x03)
                break
            elif pid == 0x03:
                self.cp, _ = rvar(data)
            elif pid == 0x04:
                mid, o = rvar(data, 1)
                self.send_pkt(0x02, wvar(mid) + wvar(0))

        print(f"[+] {self.uname}: LOGIN → CONFIG", flush=True)

        # === CONFIG state ===
        # Send client settings (0x00)
        self.send_pkt(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))

        registered = False
        while True:
            pid, data = self.recv_pkt(5)
            if pid is None:
                print("[!] Config: connection closed", flush=True)
                return False

            if pid == 0x03:  # finish_configuration
                print("[*] Config done, → PLAY", flush=True)
                break

            elif pid == 0x04:  # keep_alive
                self.send_pkt(0x04, data)

            elif pid == 0x05:  # ping
                self.send_pkt(0x05, data)

            elif pid == 0x0e:  # select_known_packs
                cnt, o = rvar(data)
                resp = b''
                for _ in range(cnt):
                    ns, o = rs(data, o)
                    n, o = rs(data, o)
                    v, o = rs(data, o)
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send_pkt(0x07, wvar(cnt) + resp)

            elif pid == 0x01:  # custom_payload
                pass

            elif pid == 0x12:  # show_dialog - Formkit registration form
                if not registered:
                    print("[!] REGISTRATION FORM DETECTED", flush=True)
                    # Extract action IDs from the NBT
                    registered = self._handle_form(data)
                    if registered:
                        print(f"[+] Registered as {self.uname} / {self.pwd}", flush=True)
                    else:
                        print("[!] Form handling failed", flush=True)
                        return False

            elif pid == 0x13:  # code_of_conduct
                self.send_pkt(0x09)

            elif pid == 0x02:  # disconnect
                m, o = rvar(data)
                txt = data[o:].decode(errors='replace')
                print(f"[!] Config kick: {txt[:200]}", flush=True)
                return False

        # === PLAY state ===
        self.send_pkt(0x03)  # finish_configuration → PLAY
        print(f"[+] {self.uname}: PLAY!", flush=True)

        # Heartbeat (tick_end = 0x0c)
        running = True
        def hb():
            while running:
                try: self.send_pkt(0x0c)
                except: break
                time.sleep(0.5)
        threading.Thread(target=hb, daemon=True).start()

        loaded = False
        ci = 0
        t0 = time.time()

        while True:
            now = time.time()
            try:
                pid, data = self.recv_pkt(1)
                if pid is None: break
            except socket.timeout:
                pid = None
            except: break

            if pid is None:
                pass
            elif pid == 0x2b:  # keep_alive
                self.send_pkt(0x1b, data)
            elif pid == 0x30:  # login (play state enter)
                if not loaded:
                    self.send_pkt(0x2b)  # player_loaded
                    self.send_pkt(0x0d, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                    loaded = True
            elif pid == 0x46:  # position
                tid, _ = rvar(data)
                self.send_pkt(0x00, wvar(tid))
            elif pid == 0x20:  # kick_disconnect
                m, o = rvar(data)
                txt = data[o:].decode(errors='replace')
                txt = re.sub(r'\xa7.', '', txt)
                try:
                    j = json.loads(txt)
                    txt = self._extract_json(j)
                except: pass
                print(f"[KICK] {txt[:300]}", flush=True)
                break
            elif pid == 0x77:  # system_chat
                msg, _ = rs(data)
                if msg.startswith("{"):
                    try:
                        j = json.loads(msg)
                        msg = self._extract_json(j)
                    except: pass
                msg = re.sub(r'\xa7.', '', msg).strip()
                if msg:
                    self.msgs.append(msg)
                    print(f"[C] {msg[:500]}", flush=True)
            elif pid == 0x3f:  # player_chat
                try:
                    o = 0
                    gi, o = rvar(data, o); o += 1
                    o += 16  # skip UUID
                    idx, o = rvar(data, o) if o < len(data) else (0, o)
                    sig_f = data[o] if o < len(data) else 0; o += 1
                    if sig_f and o < len(data):
                        sl, o = rvar(data, o)
                        hlen, o = rvar(data, o) if o < len(data) else (0, o)
                        o += hlen + 32
                    msg, _ = rs(data, o) if o < len(data) else ('', o)
                    msg = re.sub(r'\xa7.', '', msg)
                    if msg.strip():
                        self.msgs.append(msg.strip())
                        print(f"[P] {msg.strip()[:300]}", flush=True)
                except: pass
            elif pid == 0x6e:  # set_title_subtitle
                try:
                    ttype, o = rvar(data)
                    msg, _ = rs(data, o) if o < len(data) else ('', o)
                    if msg.startswith("{"):
                        try:
                            j = json.loads(msg)
                            msg = self._extract_json(j)
                        except: pass
                    msg = re.sub(r'\xa7.', '', msg).strip()
                    if msg:
                        self.msgs.append(msg)
                        print(f"[T] {msg[:300]}", flush=True)
                except: pass
            elif pid == 0x70:  # set_title_text
                try:
                    msg, _ = rs(data)
                    if msg.startswith("{"):
                        try:
                            j = json.loads(msg)
                            msg = self._extract_json(j)
                        except: pass
                    msg = re.sub(r'\xa7.', '', msg).strip()
                    if msg:
                        self.msgs.append(msg)
                        print(f"[TT] {msg[:300]}", flush=True)
                except: pass
            elif pid == 0x55:  # action_bar
                try:
                    msg, _ = rs(data)
                    if msg.startswith("{"):
                        try:
                            j = json.loads(msg)
                            msg = self._extract_json(j)
                        except: pass
                    msg = re.sub(r'\xa7.', '', msg).strip()
                    if msg:
                        self.msgs.append(msg)
                        print(f"[A] {msg[:300]}", flush=True)
                except: pass
            elif pid == 0x74:  # start_configuration
                print("[*] Back to CONFIG", flush=True)
                break
            elif pid == 0x8a:  # show_dialog in play state
                print("[!] Dialog in play!", flush=True)
            elif pid in (0x08, 0x0a, 0x0c, 0x0d, 0x2c, 0x2d):  # chunk/block/etc
                pass

            # Send commands
            if ci < len(commands) and now - t0 > 3 + ci * 4:
                cmd = commands[ci]
                print(f">>> /{cmd}", flush=True)
                self.send_pkt(0x06, wstr(cmd))  # chat_command
                ci += 1

            if ci >= len(commands) and now - t0 > 45:
                break
            if now - t0 > 55:
                break

        running = False
        self.sock.close()

        print(f"\n{'='*60}", flush=True)
        print(f"RESULTS ({len(self.msgs)} messages):", flush=True)
        print('='*60, flush=True)
        for m in self.msgs:
            print(f"  {m}", flush=True)

        return True

    def _handle_form(self, data):
        """Handle Formkit show_dialog registration form."""
        # Parse the NBT to get action IDs
        try:
            # The data starts with TAG_Compound (0x0a) - anonymousNbt
            o = 0
            if data[o] != 0x0a:  # TAG_Compound
                print(f"[!] Form doesn't start with TAG_Compound: 0x{data[o]:02X}", flush=True)
                return False
            o += 1
            # Name length (short) - anonymous NBT has name length 0
            nl = struct.unpack('>H', data[o:o+2])[0]; o += 2
            if nl > 0:
                o += nl  # skip name

            # Parse fields until TAG_End
            submit_id = None
            while o < len(data) and data[o] != 0:
                tt = data[o]; o += 1
                nl2 = struct.unpack('>H', data[o:o+2])[0]; o += 2
                name = data[o:o+nl2].decode(errors='replace') if nl2 > 0 else ''; o += nl2

                if tt == 0x09:  # TAG_List
                    lt = data[o]; o += 1
                    ll = struct.unpack('>I', data[o:o+4])[0]; o += 4

                    if name == 'actions' and lt == 0x0a:
                        for _ in range(ll):
                            # Each action is a compound
                            if data[o] != 0x0a: break
                            o += 1
                            anl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                            o += anl
                            # Look for 'id' string
                            act_id = None
                            while o < len(data) and data[o] != 0 and data[o] != 0x0a:
                                at = data[o]; o += 1
                                anl2 = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                aname = data[o:o+anl2].decode(errors='replace') if anl2 > 0 else ''; o += anl2
                                if at == 0x08 and aname == 'type':
                                    vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                    o += vl
                                elif at == 0x08 and aname == 'id':
                                    vl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                    act_id = data[o:o+vl].decode(errors='replace'); o += vl
                                elif at == 0x0a:  # compound for label
                                    # Skip label
                                    cllen = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                    # Parse until end
                                    while o < len(data) and data[o] != 0:
                                        ct = data[o]; o += 1
                                        cnl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                        cname = data[o:o+cnl].decode(errors='replace') if cnl > 0 else ''; o += cnl
                                        if ct == 0x08:
                                            cvl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                            o += cvl
                                    if o < len(data) and data[o] == 0: o += 1
                                elif at == 0x09:  # list in action (skip)
                                    llt = data[o]; o += 1
                                    lll = struct.unpack('>I', data[o:o+4])[0]; o += 4
                                    # Skip list entries
                                    for _ in range(lll):
                                        if llt == 0x08:
                                            svl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                            o += svl
                                        elif llt == 0x0a:
                                            while o < len(data) and data[o] != 0:
                                                ct = data[o]; o += 1
                                                cnl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                                cname = data[o:o+cnl].decode(errors='replace') if cnl > 0 else ''; o += cnl
                                                if ct == 0x08:
                                                    cvl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                                    o += cvl
                                            if o < len(data) and data[o] == 0: o += 1
                                else:
                                    print(f"[!] Unknown action field type 0x{at:02X} name={aname}", flush=True)
                                    # Skip by trying to continue
                            if o < len(data) and data[o] == 0: o += 1

                            if act_id and 'submit' in act_id:
                                submit_id = act_id
                elif tt == 0x0a:  # compound - skip it
                    while o < len(data) and data[o] != 0:
                        ctt = data[o]; o += 1
                        cnl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                        cname = data[o:o+cnl].decode(errors='replace') if cnl > 0 else ''; o += cnl
                        if ctt == 0x08:
                            cvl = struct.unpack('>H', data[o:o+2])[0]; o += 2
                            o += cvl
                        elif ctt == 0x0a:
                            while o < len(data) and data[o] != 0:
                                ct2 = data[o]; o += 1
                                cnl2 = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                cname2 = data[o:o+cnl2].decode(errors='replace') if cnl2 > 0 else ''; o += cnl2
                                if ct2 == 0x08:
                                    cvl2 = struct.unpack('>H', data[o:o+2])[0]; o += 2
                                    o += cvl2
                            if o < len(data) and data[o] == 0: o += 1
                    if o < len(data) and data[o] == 0: o += 1

            if not submit_id:
                # Default fallback
                print("[!] Couldn't find submit action ID, using default", flush=True)

            # Send custom_click_action (0x08)
            pkt = wstr(submit_id or "authme:prejoin-register/submit")
            pkt += wvar(2)  # 2 inputs
            pkt += wstr("password") + wstr(self.pwd)
            pkt += wstr("confirm") + wstr(self.pwd)
            self.send_pkt(0x08, pkt)
            print(f"[+] Sent registration: {self.uname}/{self.pwd}", flush=True)
            return True
        except Exception as e:
            print(f"[!] Form parse error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

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
    bot = SkyBot(suffix)
    cmds = [
        'help', 'balance', 'tradebook help', 'tradebook list',
        'shop', 'leaderboard', 'baltop', 'island',
    ]
    bot.run(cmds)
