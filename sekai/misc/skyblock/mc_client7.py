"""
Minecraft Protocol Client v7 - Proper protocol handling for 26.1.2
"""
import socket
import struct
import time
import uuid
import zlib
import json
import sys

HOST = "skyblock.chals.sekai.team"
PORT = 25565
PROTOCOL_VERSION = 775

def write_varint(value):
    out = bytearray()
    while True:
        if value & 0xFFFFFF80 == 0:
            out.append(value & 0x7F)
            return bytes(out)
        out.append((value & 0x7F) | 0x80)
        value = (value >> 7) & 0xFFFFFFFF
        if value == 0:
            out[-1] &= 0x7F
            return bytes(out)

def read_varint_data(data, offset=0):
    result = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of varint at %d" % offset)
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        shift += 7
        offset += 1
        if not (byte & 0x80):
            return result, offset

def write_string(s):
    encoded = s.encode('utf-8')
    return write_varint(len(encoded)) + encoded

def write_uuid(u):
    return struct.pack('>QQ', u.int >> 64, u.int & ((1 << 64) - 1))

class MCClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.username = "Bot_" + str(int(time.time() % 100000))
        self.my_uuid = uuid.uuid4()
        self.compression = -1
        self.running = True
        self.chat_messages = []

    def log(self, msg):
        print(msg, flush=True)

    def send_raw(self, raw_data):
        if self.compression >= 0:
            if len(raw_data) >= self.compression:
                compressed = zlib.compress(raw_data)
                frame = write_varint(len(raw_data)) + compressed
            else:
                frame = write_varint(0) + raw_data
            self.sock.sendall(write_varint(len(frame)) + frame)
        else:
            self.sock.sendall(write_varint(len(raw_data)) + raw_data)

    def send_pkt(self, pid, data=b''):
        self.send_raw(write_varint(pid) + data)

    def recv_pkt(self):
        data = b''
        while True:
            b = self.sock.recv(1)
            if not b:
                raise ConnectionError("Closed")
            data += b
            if not (b[0] & 0x80):
                break
        pkt_len, _ = read_varint_data(data)
        rest = b''
        while len(rest) < pkt_len:
            chunk = self.sock.recv(pkt_len - len(rest))
            if not chunk:
                raise ConnectionError("Closed during data")
            rest += chunk
        if self.compression >= 0:
            dlen, off = read_varint_data(rest)
            if dlen > 0:
                dec = zlib.decompress(rest[off:])
                pid, off2 = read_varint_data(dec)
                return pid, dec[off2:]
            else:
                pid, off2 = read_varint_data(rest, off)
                return pid, rest[off2:]
        else:
            pid, offset = read_varint_data(rest)
            return pid, rest[offset:]

    def read_str(self, data, offset=0):
        l, off = read_varint_data(data, offset)
        return data[off:off+l].decode('utf-8'), off+l

    def send_chat(self, message):
        timestamp = int(time.time() * 1000)
        data = (
            write_string(message) +
            struct.pack('>q', timestamp) +
            struct.pack('>q', 0) +
            write_varint(0) +
            write_varint(0) +
            bytes([0])
        )
        self.send_pkt(0x07, data)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.log("Connecting...")
        self.sock.connect((self.host, self.port))
        self.log(f"Connected as {self.username} / {self.my_uuid}")

        # === HANDSHAKE -> LOGIN ===
        self.log("\n--- Handshake ---")
        hs = write_varint(PROTOCOL_VERSION) + write_string(self.host) + struct.pack('>H', self.port) + write_varint(2)
        self.send_pkt(0x00, hs)
        self.log("Sent handshake")

        # === LOGIN START ===
        self.log("--- Login Start ---")
        ls = write_string(self.username) + write_uuid(self.my_uuid)
        self.send_pkt(0x00, ls)
        self.log("Sent login start")

        # === LOGIN STATE ===
        self.log("--- Login State ---")
        login_success = False
        self.sock.settimeout(15)
        while not login_success and self.running:
            pid, payload = self.recv_pkt()
            if pid == 0x00:
                reason, _ = self.read_str(payload, 0)
                self.log(f"  DISCONNECT: {reason[:200]}")
                return
            elif pid == 0x02:
                server_uuid = uuid.UUID(bytes=payload[:16])
                uname, off = self.read_str(payload, 16)
                self.log(f"  LOGIN SUCCESS: {uname} ({server_uuid})")
                self.log("  Sending Login Acknowledged...")
                self.send_pkt(0x03)  # Login Acknowledged -> CONFIG
                login_success = True
            elif pid == 0x03:
                self.compression, _ = read_varint_data(payload, 0)
                self.log(f"  COMPRESSION: threshold={self.compression}")
            elif pid == 0x04:
                mid, off = read_varint_data(payload, 0)
                ch, off = self.read_str(payload, off)
                self.log(f"  PLUGIN REQ: id={mid}, channel='{ch}'")
                self.send_pkt(0x02, write_varint(mid) + write_varint(0))
            else:
                self.log(f"  UNKNOWN LOGIN 0x{pid:02X}: {payload[:40].hex()}")

        if not self.running:
            return

        # === CONFIGURATION STATE ===
        self.log("\n--- Configuration State ---")
        # Send client info FIRST, before reading (required by 1.20.5+ protocol)
        self.log("  Sending Client Info...")
        info = (
            write_string("en_US") +
            bytes([12]) +
            write_varint(0) +
            bytes([1]) +
            bytes([0x7F]) +
            write_varint(1) +
            bytes([0]) +
            bytes([1]) +
            bytes([0])
        )
        self.send_pkt(0x00, info)
        self.log("  Client info sent")

        config_finish = False
        self.sock.settimeout(15)

        while not config_finish and self.running:
            try:
                pid, payload = self.recv_pkt()
            except ConnectionError:
                self.log("  [Connection lost during config]")
                break
            except socket.timeout:
                self.log("  [Timeout waiting for config packets]")
                break

            h = payload[:60].hex()

            if pid == 0x00:  # Cookie Request (serverbound 0x00 in config)
                mid, off = read_varint_data(payload, 0)
                self.log(f"  [COOKIE REQ {mid}]")
                self.send_pkt(0x01, write_varint(mid) + write_varint(0))
            elif pid == 0x01:  # Custom Payload / Plugin Message
                ch, off = self.read_str(payload, 0)
                if ch == "minecraft:brand":
                    brand_len, boff = read_varint_data(payload, off)
                    brand = payload[boff:boff+brand_len].decode('utf-8', errors='replace')
                    self.log(f"  [BRAND] {brand}")
                else:
                    self.log(f"  [PLUGIN] {ch}")
            elif pid == 0x02:  # Disconnect
                reason, _ = self.read_str(payload, 0)
                self.log(f"  DISCONNECT: {reason[:200]}")
                return
            elif pid == 0x03:  # Finish Configuration
                self.log(f"  [FINISH CONFIG] Server done!")
                config_finish = True
            elif pid == 0x04:  # Keep Alive
                self.send_pkt(0x04, payload)
                self.log(f"  [KEEPALIVE]")
            elif pid == 0x05:  # Ping
                self.log(f"  [PING]")
            elif pid == 0x07:  # Registry Data (large, skip print)
                pass
            elif pid == 0x0c:  # Feature Flags
                self.log(f"  [FEATURES] {h[:60]}")
            elif pid == 0x0d:  # Tags
                self.log(f"  [TAGS] {h[:60]}")
            elif pid == 0x0e:  # Select Known Packs
                self.log(f"  [KNOWN PACKS] {h[:60]}")
                self.send_pkt(0x0e, write_varint(0))
                self.log(f"  -> sent known packs response")
                # Also re-send client info (some servers require it after known packs)
                self.send_pkt(0x00, info)
                self.log("  -> re-sent client info")
            elif pid == 0x0f:  # Custom Report Details
                self.log(f"  [REPORT DETAILS] {h[:40]}")
            else:
                self.log(f"  [MISC 0x{pid:02X}] {h[:40]}")

        if not self.running:
            return

        # Send client info before entering play
        self.log("\n--- Sending Client Info (settings) ---")
        info = (
            write_string("en_US") +
            bytes([12]) +
            write_varint(0) +
            bytes([1]) +
            bytes([0x7F]) +
            write_varint(1) +
            bytes([0]) +
            bytes([1]) +
            bytes([0])
        )
        self.send_pkt(0x00, info)
        self.log("  Client info sent")

        # Send Finish Configuration
        self.log("--- Sending Finish Config -> PLAY ---")
        self.send_pkt(0x03)
        self.log("--- Now in PLAY state! ---")

        # === PLAY STATE ===
        self.log("\n--- Play State ---")
        self.sock.settimeout(10)

        cmds = [
            "/tradebook",
            "/tradebook help",
            "/balance",
            "/tradebook list",
        ]
        cmd_idx = 0
        cmd_timer = time.time()
        pos_ack_wait = 3  # Wait for position packet before sending commands

        while self.running:
            try:
                pid, payload = self.recv_pkt()
            except socket.timeout:
                self.log("\n  [Timeout in play]")
                break
            except ConnectionError:
                self.log("\n  [Disconnected]")
                break

            # Handle packets
            if pid == 0x27:  # Keep Alive
                self.send_pkt(0x1a, payload)
            elif pid == 0x73:  # System Chat
                try:
                    content, _ = self.read_str(payload, 0)
                    try:
                        obj = json.loads(content)
                        if isinstance(obj, dict):
                            content = obj.get('text', content)
                    except:
                        pass
                    self.log(f"  [CHAT] {content[:500]}")
                    self.chat_messages.append(content)
                except:
                    self.log(f"  [CHAT] (unparseable)")
            elif pid == 0x42:  # Position
                self.log(f"  [POSITION] spawned!")
                self.send_pkt(0x00, write_varint(0))
            elif pid == 0x2c:  # Login/Respawn
                self.log(f"  [JOIN] World loaded")
            elif pid == 0x19:  # Custom Payload
                ch, off = self.read_str(payload, 0)
                self.log(f"  [PLUGIN] {ch}")
            elif pid == 0x1d:  # Kick
                reason, _ = self.read_str(payload, 0)
                self.log(f"  [KICK] {reason[:300]}")
                break
            elif pid == 0x01:  # Spawn Entity
                pass
            elif pid == 0x28:  # Chunk Data
                pass
            elif pid == 0x2b:  # Light Update
                pass
            elif pid == 0x50:  # Server Data
                self.log(f"  [SERVER DATA]")
            else:
                pass  # skip unknown

            # Send commands after a delay
            if cmd_idx < len(cmds) and time.time() - cmd_timer > 3:
                cmd = cmds[cmd_idx]
                self.log(f"\n>>> / {cmd}")
                self.send_chat(cmd)
                cmd_idx += 1
                cmd_timer = time.time()

            if cmd_idx >= len(cmds) and time.time() - cmd_timer > 10:
                break

        self.log("\n=== Chat messages received ===")
        for i, m in enumerate(self.chat_messages):
            self.log(f"  {i+1}. {m[:300]}")

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

if __name__ == "__main__":
    client = MCClient(HOST, PORT)
    try:
        client.run()
    except Exception as e:
        print(f"\nFATAL: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\nDone", flush=True)
