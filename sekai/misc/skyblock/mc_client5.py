"""
Minecraft Protocol Client v5 - full login + configuration + play
"""
import socket
import struct
import time
import uuid
import zlib

HOST = "skyblock.chals.sekai.team"
PORT = 25565
PROTOCOL_VERSION = 775

def write_varint(value):
    out = bytearray()
    while True:
        if value & 0x7FFFFFFF == 0:
            out.append(0)
            return bytes(out)
        out.append((value & 0x7F) | 0x80)
        value = (value >> 7) & 0x7FFFFFFF
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
        self.compression_threshold = -1
        self.state = "HANDSHAKE"  # HANDSHAKE, LOGIN, CONFIG, PLAY
        self.running = True

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        print("Connecting...")
        self.sock.connect((self.host, self.port))
        print(f"Connected as {self.username} / {self.my_uuid}")

    def send_raw(self, raw_data):
        """Send a packet with proper compression handling"""
        if self.compression_threshold >= 0:
            # Compression format: DataLength + (compressed or raw) data
            if len(raw_data) >= self.compression_threshold:
                compressed = zlib.compress(raw_data)
                compressed_data = write_varint(len(raw_data)) + compressed
            else:
                compressed_data = write_varint(0) + raw_data
            self.sock.sendall(write_varint(len(compressed_data)) + compressed_data)
        else:
            self.sock.sendall(write_varint(len(raw_data)) + raw_data)

    def send_packet(self, state, packet_id, data=b''):
        raw = write_varint(packet_id) + data
        state_name = self.state
        self.send_raw(raw)

    def recv_packet(self):
        """Read and decompress one packet. Returns (packet_id, data_bytes)"""
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

        # Handle compression
        if self.compression_threshold >= 0:
            data_length, offset = read_varint_data(rest)
            if data_length > 0:
                decompressed = zlib.decompress(rest[offset:])
                pkt_id, off2 = read_varint_data(decompressed)
                return pkt_id, decompressed[off2:]
            else:
                pkt_id, off2 = read_varint_data(rest, offset)
                return pkt_id, rest[off2:]
        else:
            pkt_id, offset = read_varint_data(rest)
            return pkt_id, rest[offset:]

    def read_string(self, data, offset=0):
        """Read a Minecraft String from data at offset"""
        length, offset = read_varint_data(data, offset)
        s = data[offset:offset+length].decode('utf-8')
        return s, offset + length

    def run(self):
        self.connect()

        # === HANDSHAKE -> LOGIN ===
        self.state = "HANDSHAKE"
        print("\n--- Handshake ---")
        handshake = (write_varint(PROTOCOL_VERSION) + write_string(self.host) +
                     struct.pack('>H', self.port) + write_varint(2))
        self.send_packet("HANDSHAKE", 0x00, handshake)
        self.state = "LOGIN"

        # === LOGIN START ===
        print("--- Login Start ---")
        login_start = write_string(self.username) + write_uuid(self.my_uuid)
        self.send_packet("LOGIN", 0x00, login_start)

        # === Process LOGIN state packets ===
        print("--- Login Sequence ---")
        login_complete = False

        while self.state == "LOGIN" and self.running:
            pkt_id, payload = self.recv_packet()
            print(f"  [LOGIN] Packet 0x{pkt_id:02X}, {len(payload)} bytes")

            if pkt_id == 0x00:  # Login Disconnect
                reason, _ = self.read_string(payload, 0)
                print(f"  *** DISCONNECT: {reason[:200]} ***")
                self.running = False
                break
            elif pkt_id == 0x02:  # Login Success
                print(f"  *** LOGIN SUCCESS ***")
                # Parse UUID and username
                server_uuid = uuid.UUID(bytes=payload[:16])
                uname, off = self.read_string(payload, 16)
                print(f"      Server UUID: {server_uuid}, Username: {uname}")
                login_complete = True
            elif pkt_id == 0x03:  # Set Compression
                self.compression_threshold, _ = read_varint_data(payload, 0)
                print(f"  *** COMPRESSION: threshold={self.compression_threshold} ***")
            elif pkt_id == 0x04:  # Login Plugin Request
                msg_id, off = read_varint_data(payload, 0)
                channel, off = self.read_string(payload, off)
                print(f"  *** PLUGIN REQUEST: msg_id={msg_id}, channel={channel} ***")
                # Respond with empty data
                resp = write_varint(msg_id) + write_varint(0)
                self.send_packet("LOGIN", 0x02, resp)
            else:
                print(f"  --- Unknown LOGIN packet 0x{pkt_id:02X} ---")
                print(f"      hex: {payload[:40].hex()}")

            if login_complete:
                # Send Login Acknowledged to enter CONFIGURATION
                print("\n--- Sending Login Acknowledged -> CONFIG ---")
                self.send_packet("LOGIN", 0x03, b'')
                self.state = "CONFIG"
                break

        # === CONFIGURATION state ===
        print("\n--- Configuration Sequence ---")
        config_done = False

        while self.state == "CONFIG" and self.running:
            pkt_id, payload = self.recv_packet()
            print(f"  [CONFIG] Packet 0x{pkt_id:02X}, {len(payload)} bytes")
            payload_hex = payload[:60].hex()

            if pkt_id == 0x00:  # Plugin Message in CONFIG (or disconnect)
                # Try to determine which
                try:
                    channel, off = self.read_string(payload, 0)
                    print(f"  *** CONFIG PLUGIN: channel={channel}")
                    # If it starts with minecraft: or has a colon, it's a plugin message
                except:
                    print(f"  *** CONFIG DISCONNECT possibly ***")
                    pass
            elif pkt_id == 0x01:  # Maybe Plugin Message instead of disconnect
                try:
                    channel, off = self.read_string(payload, 0)
                    print(f"  *** CONFIG PLUGIN (id=0x01): channel={channel}")
                    data = payload[off:]
                    if channel == "minecraft:brand":
                        brand_len, brand_off = read_varint_data(data, 0)
                        brand = data[brand_off:brand_off+brand_len].decode('utf-8', errors='replace')
                        print(f"      Brand: {brand}")
                except Exception as e:
                    print(f"  *** CONFIG UNKNOWN: {e}")
            elif pkt_id == 0x02:  # Finish Configuration / Server Data / Disconnect?
                try:
                    reason, _ = self.read_string(payload, 0)
                    print(f"  *** CONFIG packet 0x02: string='{reason[:100]}' ***")
                    if "disconnect" in reason.lower():
                        print(f"      -> DISCONNECT")
                        self.running = False
                        break
                except:
                    print(f"  *** CONFIG packet 0x02: non-string data: {payload_hex}")
            elif pkt_id == 0x03:  # Config Features / Keep Alive?
                print(f"  *** CONFIG packet 0x03: {payload_hex}")
                # Could be keep alive - echo back
                self.send_packet("CONFIG", 0x03, payload)
            elif pkt_id in (0x12, 0x21):  # Keep Alive
                print(f"  *** KEEP ALIVE ***")
                self.send_packet("CONFIG", pkt_id, payload)
            elif pkt_id == 0x5F:  # System Chat
                content, _ = self.read_string(payload, 0)
                print(f"  [CHAT] {content[:200]}")
            elif pkt_id >= 0x10:  # Higher IDs likely config settings (tags, features, etc.)
                print(f"  *** CONFIG META packet 0x{pkt_id:02X}: {payload_hex}")
                # These are declarations of features/tags/recipes etc - just log
            else:
                print(f"  *** Unknown CONFIG packet 0x{pkt_id:02X}: {payload_hex}")

        # Send Finish Configuration to enter PLAY
        if self.state == "CONFIG":
            print("\n--- Sending Finish Configuration -> PLAY ---")
            # In 1.20.5+, the serverbound Finish Configuration might have specific data
            # Could be empty, or have Known Pack data
            # Try with just an empty Known Packs array
            self.send_packet("CONFIG", 0x03, write_varint(0))  # 0 known packs
            self.state = "PLAY"
            print("--- Now in PLAY state! ---")

        # === PLAY state ===
        print("\n--- PLAY State ---")
        chat_cmds = [
            "/tradebook",
            "/tradebook help",
            "/balance",
            "/help",
            "/tradebook list",
        ]
        cmd_idx = 0

        while self.running:
            try:
                pkt_id, payload = self.recv_packet()
                pkt_name = "UNKNOWN"

                if pkt_id == 0x12:  # Keep Alive
                    self.send_packet("PLAY", 0x12, payload)
                    pkt_name = "KEEP ALIVE (echoed)"

                elif pkt_id == 0x5F:  # System Chat Message (1.19+)
                    content, _ = self.read_string(payload, 0)
                    pkt_name = f"CHAT: {content[:300]}"

                elif pkt_id == 0x3B:  # Synchronize Player Position
                    pkt_name = "PLAYER POSITION/SYNC"

                elif pkt_id == 0x3C:  # Chunk Data
                    pkt_name = "CHUNK DATA"

                elif pkt_id == 0x01:  # Disconnect
                    reason, _ = self.read_string(payload, 0)
                    pkt_name = f"DISCONNECT: {reason[:200]}"
                    self.running = False

                elif pkt_id == 0x0E:  # Set Container Content
                    pkt_name = "CONTAINER CONTENT"

                elif pkt_id == 0x0F:  # Set Container Slot
                    pkt_name = "CONTAINER SLOT"

                else:
                    pkt_name = f"0x{pkt_id:02X} ({len(payload)} bytes)"

                print(f"  [{pkt_name}]")

                # Send commands at intervals
                if cmd_idx < len(chat_cmds):
                    cmd = chat_cmds[cmd_idx]
                    print(f"\n>>> Sending: {cmd}")
                    self.send_chat(cmd)
                    cmd_idx += 1

            except socket.timeout:
                print("\n[Timeout]")
                break
            except ConnectionError:
                print("\n[Connection closed]")
                break

    def send_chat(self, message):
        """Send a chat message in PLAY state (unsigned, 1.19+ format)"""
        timestamp = int(time.time() * 1000)
        # For unsigned chat in offline mode:
        # message (String), timestamp (Long), salt (Long), signature (byte array with 0 length),
        # message count (VarInt), acknowledged (BitSet - 1 byte per message, but 0 length is fine)
        packet_data = (
            write_string(message) +
            struct.pack('>q', timestamp) +
            struct.pack('>q', 0) +
            write_varint(0) +       # signature length = 0
            write_varint(0) +       # message count = 0
            bytearray([0])          # acknowledged bits (empty)
        )
        self.send_packet("PLAY", 0x05, packet_data)

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
