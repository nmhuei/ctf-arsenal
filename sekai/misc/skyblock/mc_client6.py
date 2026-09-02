"""
Minecraft Protocol Client v6 - Correct packet IDs for protocol 775
Based on 1.21.4 (protocol 769) packet mappings
"""
import socket
import struct
import time
import uuid
import zlib
import json

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
            raise ValueError("Unexpected end of varint")
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
        self.state = "HANDSHAKE"
        self.running = True
        self.chat_messages = []
        self.config_done = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        print("Connecting...")
        self.sock.connect((self.host, self.port))
        print(f"Connected as {self.username} / {self.my_uuid}")

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

    def send_pkt(self, packet_id, data=b''):
        raw = write_varint(packet_id) + data
        self.send_raw(raw)

    def recv_pkt(self):
        data = b''
        while True:
            b = self.sock.recv(1)
            if not b:
                raise ConnectionError("Closed")
            data += b
            if not (b[0] & 0x80):
                break
        length, _ = read_varint_data(data)
        rest = b''
        while len(rest) < length:
            chunk = self.sock.recv(length - len(rest))
            if not chunk:
                raise ConnectionError("Closed")
            rest += chunk
        if self.compression >= 0:
            dlen, off = read_varint_data(rest)
            if dlen > 0:
                dec = zlib.decompress(rest[off:])
                pkt_id, off2 = read_varint_data(dec)
                return pkt_id, dec[off2:]
            else:
                pkt_id, off2 = read_varint_data(rest, off)
                return pkt_id, rest[off2:]
        else:
            pkt_id, offset = read_varint_data(rest)
            return pkt_id, rest[offset:]

    def read_str(self, data, offset=0):
        l, off = read_varint_data(data, offset)
        return data[off:off+l].decode('utf-8'), off+l

    # === CONFIG state helpers (1.21.4 IDs) ===
    def send_config_finish(self):
        self.send_pkt(0x03)
        print("  [->] Finish Configuration")

    def send_config_keepalive(self, data):
        self.send_pkt(0x04, data)

    def send_config_client_info(self):
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
        print("  [->] Client Info")

    def send_known_packs(self, data):
        """Respond to select_known_packs - send back an empty list"""
        # Server sends a list of known packs. Client responds with an
        # empty array (varint 0) meaning "I don't have any of those"
        # Response packet is 0x0e serverbound
        # Actually in 1.21.4 serverbound CONFIG: 0x0e = select_known_packs
        self.send_pkt(0x0e, write_varint(0))
        print("  [->] Known Packs (empty response)")

    def handle_plugin_message(self, channel, data):
        print(f"  [PLUGIN] {channel}")
        if channel == "minecraft:brand":
            brand_len, off = read_varint_data(data, 0)
            brand = data[off:off+brand_len].decode('utf-8', errors='replace')
            print(f"    Brand: {brand}")

    def run(self):
        self.connect()

        # === HANDSHAKE -> LOGIN ===
        self.state = "HANDSHAKE"
        print("\n--- Handshake ---")
        hs = write_varint(PROTOCOL_VERSION) + write_string(self.host) + struct.pack('>H', self.port) + write_varint(2)
        self.send_pkt(0x00, hs)
        self.state = "LOGIN"

        # === LOGIN START ===
        print("--- Login Start ---")
        ls = write_string(self.username) + write_uuid(self.my_uuid)
        self.send_pkt(0x00, ls)

        # === LOGIN STATE ===
        print("--- Login State ---")
        while self.state == "LOGIN" and self.running:
            pid, payload = self.recv_pkt()
            if pid == 0x00:  # Login Disconnect
                reason, _ = self.read_str(payload, 0)
                print(f"  DISCONNECT: {reason[:200]}")
                self.running = False
            elif pid == 0x02:  # Login Success
                server_uuid = uuid.UUID(bytes=payload[:16])
                uname, off = self.read_str(payload, 16)
                print(f"  LOGIN SUCCESS: {uname} ({server_uuid})")
                self.state = "CONFIG"
                print("\n--- Sending Login Acknowledged -> CONFIG ---")
                # Login Acknowledged (serverbound 0x03 in LOGIN state)
                self.send_pkt(0x03)
            elif pid == 0x03:  # Set Compression
                self.compression, _ = read_varint_data(payload, 0)
                print(f"  COMPRESSION: threshold={self.compression}")
            elif pid == 0x04:  # Login Plugin Request
                mid, off = read_varint_data(payload, 0)
                ch, off = self.read_str(payload, off)
                print(f"  PLUGIN REQ: id={mid}, channel='{ch}'")
                self.send_pkt(0x02, write_varint(mid) + write_varint(0))
            else:
                print(f"  UNKNOWN LOGIN 0x{pid:02X}: {payload[:40].hex()}")

        # === CONFIGURATION STATE ===
        print("\n--- Configuration State ---")
        self.config_client_info_sent = False

        while self.state == "CONFIG" and self.running:
            try:
                pid, payload = self.recv_pkt()
            except (socket.timeout, ConnectionError) as e:
                print(f"  [CONFIG END] {e}")
                break
            h = payload[:60].hex()

            if pid == 0x00:  # Cookie Request
                print(f"  COOKIE REQ")
                mid, off = read_varint_data(payload, 0)
                self.send_pkt(0x01, write_varint(mid) + write_varint(0))
                self.send_config_client_info()
                self.config_client_info_sent = True
            elif pid == 0x01:  # Custom Payload (Plugin Message)
                ch, off = self.read_str(payload, 0)
                self.handle_plugin_message(ch, payload[off:])
                if not self.config_client_info_sent:
                    self.send_config_client_info()
                    self.config_client_info_sent = True
            elif pid == 0x02:  # Disconnect
                reason, _ = self.read_str(payload, 0)
                print(f"  DISCONNECT: {reason[:200]}")
                self.running = False
            elif pid == 0x03:  # Finish Configuration
                print(f"  CONFIG FINISH -> Ready for PLAY")
                self.config_done = True
                break
            elif pid == 0x04:  # Keep Alive
                self.send_config_keepalive(payload)
            elif pid == 0x05:  # Ping
                ping_id, _ = read_varint_data(payload, 0)
                print(f"  PING: id={ping_id}")
            elif pid == 0x07:  # Registry Data - important but verbose
                pass
            elif pid == 0x0c:  # Feature Flags
                print(f"  FEATURE FLAGS: {h[:60]}")
                if not self.config_client_info_sent:
                    self.send_config_client_info()
                    self.config_client_info_sent = True
            elif pid == 0x0d:  # Tags
                print(f"  TAGS: {h[:60]}")
            elif pid == 0x0e:  # select_known_packs
                print(f"  SELECT KNOWN PACKS: {h[:60]}")
                self.send_known_packs(payload)
            elif pid in (0x08, 0x09, 0x0a, 0x0b, 0x0f, 0x10):
                print(f"  META 0x{pid:02X}: {h[:40]}")
            else:
                print(f"  UNKNOWN CONFIG 0x{pid:02X}: {h[:40]}")

            if self.config_done:
                self.state = "PLAY"
                break

        if self.state == "CONFIG":
            print("\n--- Sending Finish Configuration -> PLAY ---")
            self.send_config_finish()
            time.sleep(0.5)
            self.state = "PLAY"
            print("--- Now in PLAY state! ---")

        # === PLAY STATE ===
        print("\n--- Play State ---")
        cmds = [
            "/tradebook",
            "/tradebook help",
            "/balance",
            "/tradebook list",
        ]
        cmd_idx = 0
        cmd_timer = time.time()

        while self.running:
            try:
                pid, payload = self.recv_pkt()
            except socket.timeout:
                print("\n[Timeout]")
                break
            except ConnectionError:
                print("\n[Disconnected]")
                break

            # Handle based on 1.21.4 IDs (may differ for 26.1.2)
            if pid == 0x27:  # Keep Alive (1.21.4)
                self.send_pkt(0x1a, payload)
                continue

            elif pid == 0x73:  # System Chat (1.21.4)
                try:
                    content, _ = self.read_str(payload, 0)
                    # Try to parse as JSON
                    try:
                        obj = json.loads(content)
                        if isinstance(obj, dict):
                            content = obj.get('text', content)
                    except:
                        pass
                    print(f"  [CHAT] {content[:500]}")
                    self.chat_messages.append(content)
                except:
                    print(f"  [CHAT] (unparseable)")

            elif pid == 0x42:  # Position
                print(f"  [POSITION] (spawned)")
                # Send position ack
                self.send_pkt(0x00, write_varint(0))

            elif pid == 0x19:  # Custom Payload
                ch, off = self.read_str(payload, 0)
                print(f"  [PLUGIN] {ch}")

            elif pid == 0x2c:  # Login (world data - spawn info)
                # After receiving login packet (different from position), we're fully in play
                if cmd_idx == 0:
                    cmd_idx = 1  # Skip first command, wait for spawn
                print(f"  [LOGIN/WORLD JOIN]")

            elif pid == 0x01:  # Spawn Entity
                pass  # Ignore

            elif pid == 0x1d:  # Kick Disconnect
                reason, _ = self.read_str(payload, 0)
                print(f"  [KICK] {reason[:200]}")
                self.running = False

            elif pid == 0x2b:  # Update Light
                pass
            elif pid == 0x28:  # Chunk Data
                pass
            elif pid == 0x50:  # Server Data
                print(f"  [SERVER DATA]")
            else:
                # Skip unknown packets silently (there will be many)
                pass

            # Send commands at intervals
            if cmd_idx < len(cmds) and time.time() - cmd_timer > 3:
                cmd = cmds[cmd_idx]
                print(f"\n>>> / {cmd}")
                self.send_chat(cmd)
                cmd_idx += 1
                cmd_timer = time.time()

            if cmd_idx >= len(cmds):
                # Wait a bit for responses
                if time.time() - cmd_timer > 8:
                    break

        print("\n=== Chat messages received ===")
        for i, m in enumerate(self.chat_messages):
            print(f"  {i+1}. {m[:300]}")
        self.close()

    def send_chat(self, message):
        """Send chat message in PLAY state"""
        timestamp = int(time.time() * 1000)
        data = (
            write_string(message) +  # message
            struct.pack('>q', timestamp) +  # timestamp
            struct.pack('>q', 0) +  # salt = 0
            write_varint(0) +  # signature length = 0 (unsigned)
            write_varint(0) +  # message count = 0
            bytes([0])  # acknowledged (empty bitset)
        )
        # In 1.21.4, chat is ID 0x07 serverbound
        self.send_pkt(0x07, data)

    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    client = MCClient(HOST, PORT)
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("Done")
