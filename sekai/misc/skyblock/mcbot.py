#!/usr/bin/env python3
"""
Minecraft Protocol Client for Paper 26.1.2 (protocol 775)
"""
import socket, struct, json, threading, time, random, zlib, hashlib, sys

HOST = 'skyblock.chals.sekai.team'
PORT = 25565

class MCBot:
    def __init__(self, host=HOST, port=PORT, username=None):
        self.host = host; self.port = port
        self.username = username or f'bot{random.randint(10000,99999)}'
        self.sock = None; self.comp = -1
        self.running = False; self.state = 'HANDSHAKING'
        self.chat_log = []; self._cbs = {'play': [], 'chat': [], 'disc': []}
        self.config_started = False

    def on(self, ev, cb): self._cbs.setdefault(ev, []).append(cb)

    def connect(self):
        print(f'[+] {self.username}: connecting...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((self.host, self.port))
        self._send(0x00, self._v(775) + self._s(self.host) + struct.pack('>H', self.port) + self._v(2))
        self.state = 'LOGIN'
        self._send(0x00, self._s(self.username) + self._offline_uuid(self.username))
        self.running = True
        threading.Thread(target=self._reader, daemon=True).start()
        for _ in range(200):
            time.sleep(0.1)
            if self.state == 'PLAY': return True
            if not self.running: break
            if _ % 50 == 0: print(f'[.] waiting for PLAY... state={self.state}')
        return False

    def chat(self, msg):
        if self.state != 'PLAY': return
        if msg.startswith('/'):
            self._send(0x06, self._s(msg))
        else:
            ts = int(time.time() * 1000)
            d = self._s(msg) + struct.pack('>q', ts) + struct.pack('>q', 0)
            d += self._v(0) + self._v(0) + bytes(3) + struct.pack('B', 0)
            self._send(0x08, d)

    def disconnect(self):
        self.running = False
        try: self.sock.close()
        except: pass

    def _v(self, v):
        b = b''
        while True:
            t = v & 0x7F; v >>= 7
            b += struct.pack('B', t | (0x80 if v else 0))
            if v == 0: break
        return b

    def _vs(self, v):
        s = 0
        while True:
            s += 1
            v >>= 7
            if v == 0:
                return s

    def _rv(self):
        r = 0; s = 0
        while True:
            b = self.sock.recv(1)
            if not b: raise ConnectionError()
            v = b[0]; r |= (v & 0x7F) << s; s += 7
            if not (v & 0x80): return r

    def _s(self, s): e = s.encode('utf-8'); return self._v(len(e)) + e
    def _sfb(self, d):
        if not d: return ''
        l = self._vfb(d); h = self._vs(l)
        return d[h:h+l].decode('utf-8', errors='replace') if h+l <= len(d) else ''

    def _vfb(self, d):
        r = 0; s = 0; i = 0
        while i < len(d):
            v = d[i]; r |= (v & 0x7F) << s; s += 7; i += 1
            if not (v & 0x80): return r
        return r

    def _offline_uuid(self, name):
        d = hashlib.md5(f'OfflinePlayer:{name}'.encode()).digest()
        b = bytearray(d); b[6] = (b[6] & 0x0f) | 0x30; b[8] = (b[8] & 0x3f) | 0x80
        return bytes(b)

    def _recv_n(self, n):
        d = b''
        while len(d) < n:
            c = self.sock.recv(n - len(d))
            if not c: raise ConnectionError()
            d += c
        return d

    def _send_raw(self, data): self.sock.sendall(self._v(len(data)) + data)

    def _send(self, pid, data):
        raw = self._v(pid) + data
        if self.comp > 0 and len(raw) >= self.comp:
            c = zlib.compress(raw); out = self._v(len(raw)) + c
        elif self.comp > 0: out = self._v(0) + raw
        else: out = raw
        self._send_raw(out)

    def _reader(self):
        try:
            while self.running:
                pl = self._rv()
                data = self._recv_n(pl)
                if self.comp > 0:
                    ul = self._vfb(data); h = self._vs(ul)
                    payload = data[h:]
                    if ul > 0: payload = zlib.decompress(payload)
                else: payload = data

                pid = self._vfb(payload)
                body = payload[self._vs(pid):]

                if self.state == 'LOGIN' or self.state == 'CONFIG':
                    print(f'[P {self.state} 0x{pid:02X}] len={len(body)}')
                    if pid > 0x10 and body and len(body) < 100:
                        print(f'   data={body.hex()[:100]}')

                if self.state == 'LOGIN': self._on_login(pid, body)
                elif self.state == 'CONFIG': self._on_config(pid, body)
                elif self.state == 'PLAY': self._on_play(pid, body)
        except Exception as e:
            if self.running:
                print(f'[!] {self.username}: {type(e).__name__}: {e}')
                self.running = False

    # ===== LOGIN =====
    def _on_login(self, pid, data):
        if pid == 0x03:  # Compression
            self.comp = self._vfb(data)
        elif pid == 0x02:  # Login success
            self._send(0x03, b'')  # Login Acknowledged
            self.state = 'CONFIG'
            self.config_started = time.time()
            # Timeout: force PLAY after 10s
            threading.Thread(target=self._wait_config, daemon=True).start()
        elif pid == 0x04:  # Login Plugin Request
            mid = self._vfb(data)
            self._send(0x02, self._v(mid))
        elif pid == 0x00:  # Disconnect
            print(f'[!] Login rejected: {self._sfb(data)}')
            self.running = False

    def _wait_config(self):
        time.sleep(10)
        if self.state == 'CONFIG':
            print(f'[!] Config timeout -> forced PLAY')
            self.state = 'PLAY'
            for cb in self._cbs.get('play', []): cb()

    # ===== CONFIG =====
    def _on_config(self, pid, data):
        if pid == 0x03:  # Finish configuration
            self._send(0x03, b'')  # Ack → PLAY
            self.state = 'PLAY'
            for cb in self._cbs.get('play', []): cb()
        elif pid == 0x04:  # Keep alive
            self._send(0x04, data)
        elif pid == 0x02:  # Disconnect
            print(f'[!] Config: {self._sfb(data)}')
            self.running = False
        # Ignore other config packets (registry_data, tags, etc.)

    # ===== PLAY =====
    def _on_play(self, pid, data):
        if pid == 0x2B:  # Keep alive
            self._send(0x1B, data)
        elif pid == 0x77:  # System chat
            self._on_chat(self._sfb(data))
        elif pid == 0x3F:  # Player chat
            try:
                pos = 0
                gi = self._vfb(data[pos:]); pos += self._vs(gi)
                pos += 16  # sender UUID
                idx = self._vfb(data[pos:]) if pos < len(data) else 0; pos += self._vs(idx)
                sig_f = data[pos] if pos < len(data) else 0; pos += 1
                if sig_f and pos < len(data):
                    sl = self._vfb(data[pos:]); pos += self._vs(sl)
                    # Skip past header/body digest
                    if data[pos:pos+1]:
                        hlen = self._vfb(data[pos:]); pos += self._vs(hlen)
                        pos += hlen if pos + hlen <= len(data) else 0
                        pos += 32  # body digest
                msg = self._sfb(data[pos:]) if pos < len(data) else ''
                if msg: self._on_chat(msg)
            except: pass
        elif pid == 0x1A:  # Disconnect
            print(f'[!] Kicked: {self._sfb(data)}')
            self.running = False

    def _on_chat(self, raw):
        if not raw: return
        try:
            obj = json.loads(raw)
            text = self._extract(obj)
        except: text = raw
        if text:
            text = text.replace('\xa7', '').strip()
            while '\xa7' in text:
                i = text.index('\xa7')
                text = text[:i] + text[i+2:]
            if text:
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        print(f'[CHAT] {line}')
                        self.chat_log.append(line)
                        for cb in self._cbs.get('chat', []): cb(line)

    def _extract(self, obj):
        if isinstance(obj, str): return obj
        if isinstance(obj, dict):
            parts = []
            if 'text' in obj: parts.append(obj['text'])
            if 'extra' in obj:
                for e in obj['extra']: parts.append(self._extract(e))
            if 'translate' in obj: parts.append(str(obj.get('with', '')))
            return ''.join(parts)
        return str(obj)


if __name__ == '__main__':
    bot = MCBot(username=f'recon{random.randint(1000,9999)}')

    def on_play():
        print(f'[+] {bot.username}: PLAY state!')
        time.sleep(2)

        def run():
            cmds = [
                '/help',
                '/tradebook help',
                '/tradebook list',
                '/balance',
                '/tradebook info dirt',
                '/tradebook info cobblestone',
                '/tradebook info stone',
                '/tradebook info oak_log',
                '/tradebook info iron_ingot',
                '/tradebook info gold_ingot',
                '/tradebook info diamond',
                '/tradebook info emerald',
                '/tradebook info netherite_ingot',
                '/tradebook info wheat',
                '/tradebook info bread',
                '/tradebook info bone',
                '/tradebook info string',
                '/tradebook info ender_pearl',
                '/tradebook info slime_ball',
                '/tradebook info obsidian',
                '/tradebook info elytra',
                '/tradebook info shulker_shell',
                '/leaderboard',
                '/baltop',
                '/shop',
            ]
            for cmd in cmds:
                bot.chat(cmd)
                time.sleep(random.uniform(1.5, 2.0))
            print('\n[*] Commands sent')
        threading.Thread(target=run, daemon=True).start()

    bot.on('play', on_play)
    if bot.connect():
        time.sleep(30)
        print('\n' + '='*60)
        print('CHAT LOG')
        print('='*60)
        for line in bot.chat_log:
            print(f'  {line}')
        bot.disconnect()
    else:
        print('FAILED')
