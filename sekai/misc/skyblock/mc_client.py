"""
Minimal Minecraft Protocol Client - for connecting to 26.1.2 servers
Implementation of the bare minimum to connect and send chat messages
"""
import socket
import struct
import json
import threading
import time
import uuid
import sys

HOST = "skyblock.chals.sekai.team"
PORT = 25565
PROTOCOL_VERSION = 775  # Minecraft 26.1.2

class MinecraftClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.socket = None
        self.compression_threshold = -1
        self.running = False

    # === VarInt utilities ===
    @staticmethod
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

    @staticmethod
    def read_varint(data, offset=0):
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

    @staticmethod
    def write_string(s):
        encoded = s.encode('utf-8')
        return MinecraftClient.write_varint(len(encoded)) + encoded

    @staticmethod
    def write_ushort(v):
        return struct.pack('>H', v)

    # === Packet utilities ===
    def send_packet(self, packet_id, data=b''):
        raw = self.write_varint(packet_id) + data
        self.send_raw(raw)

    def send_raw(self, data):
        if self.compression_threshold >= 0:
            # With compression
            if len(data) >= self.compression_threshold:
                # Compressed
                import zlib
                compressed = zlib.compress(data)
                packet = self.write_varint(len(data)) + compressed
            else:
                # Uncompressed (threshold not reached)
                packet = self.write_varint(0) + data
            full = self.write_varint(len(packet)) + packet
        else:
            full = self.write_varint(len(data)) + data
        self.socket.sendall(full)

    def read_packet(self):
        """Read one packet, returns (packet_id, data)"""
        # Read packet length
        length, _ = self.read_varint(self._read_fully(1))
        # Continue reading until we have the full length
        data = self._read_fully(length)

        if self.compression_threshold >= 0:
            # With compression
            data_length, offset = self.read_varint(data)
            if data_length > 0:
                # Data is compressed
                import zlib
                uncompressed = zlib.decompress(data[offset:])
                packet_id, _ = self.read_varint(uncompressed)
                return packet_id, uncompressed[self._varint_size(uncompressed, 0):]
            else:
                # Data is uncompressed
                packet_id, offset = self.read_varint(data, offset)
                return packet_id, data[offset:]
        else:
            packet_id, offset = self.read_varint(data)
            return packet_id, data[offset:]

    def _read_fully(self, length):
        result = bytearray()
        while len(result) < length:
            chunk = self.socket.recv(length - len(result))
            if not chunk:
                raise ConnectionError("Connection closed")
            result.extend(chunk)
        return bytes(result)

    @staticmethod
    def _varint_size(data, offset):
        size = 0
        while (data[offset + size] & 0x80) != 0:
            size += 1
        return size + 1

    # === High-level protocol ===
    def handshake(self, next_state=2):  # 2 = LOGIN
        packet = (
            self.write_varint(PROTOCOL_VERSION) +
            self.write_string(self.host) +
            self.write_ushort(self.port) +
            self.write_varint(next_state)
        )
        self.send_packet(0x00, packet)

    def login_start(self):
        self.send_packet(0x00, self.write_string(self.username))

    def send_chat_message(self, message):
        """Send a chat message in PLAY state (1.19+ format)"""
        timestamp = int(time.time() * 1000)
        # Unsigned chat message format (for offline mode)
        packet_data = (
            self.write_string(message) +
            struct.pack('>q', timestamp) +  # timestamp as long
            struct.pack('>q', 0) +  # salt = 0
            self.write_varint(0) +  # signature length = 0 (unsigned)
            self.write_varint(0) +  # offset = 0
            bytearray([0])  # acknowledged bit set (empty)
        )
        self.send_packet(0x05, packet_data)

    # === Connection handling ===
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.connect((self.host, self.port))

        # Step 1: Handshake -> LOGIN state
        self.handshake(next_state=2)

        # Step 2: Login Start
        self.login_start()

        # Step 3: Handle login sequence
        self.running = True
        while self.running:
            try:
                packet_id, data = self.read_packet()
                self.handle_packet(packet_id, data)
            except Exception as e:
                print(f"[!] Error reading packet: {e}")
                break

    def handle_packet(self, packet_id, data):
        print(f"[PACKET] ID=0x{packet_id:02X}, len={len(data)} bytes")

        if packet_id == 0x02:  # Login Success (1.20+)
            # UUID (as int array), username, properties count, ...
            print(f"[LOGIN] Login success!")
            offset = 0
            # In 1.20.2+, login success has: UUID (int array), username, properties...
            # Actually for 1.19.3+, it changed. Let me try a simpler parse
            print(f"[LOGIN] Raw data: {data[:60].hex()}")

        elif packet_id == 0x03:  # Set Compression
            self.compression_threshold, _ = self.read_varint(data)
            print(f"[COMPRESSION] Threshold: {self.compression_threshold}")

        elif packet_id == 0x04:  # Login Plugin Request
            msg_id, offset = self.read_varint(data)
            channel_len, offset = self.read_varint(data, offset)
            channel = data[offset:offset+channel_len].decode('utf-8')
            print(f"[LOGIN PLUGIN] msg_id={msg_id}, channel={channel}")
            # Respond with Login Plugin Response (0x02)
            response = self.write_varint(msg_id) + self.write_varint(0)  # no data
            self.send_packet(0x02, response)

        elif packet_id == 0x0C:  # Login Acknowledged required
            print("[CONFIG] Login Acknowledged received")
            # Send Configuration Acknowledged
            # Actually in 1.20.2+, after login, server sends Login Acknowledged
            # Then it transitions to CONFIGURATION state

        elif packet_id == 0x5F:  # System Chat Message (PLAY state)
            self.handle_system_chat(data)

        elif packet_id == 0x12:  # Keep Alive
            self.handle_keepalive(data)

        elif packet_id == 0x21:  # Keep Alive (PLAY)
            self.handle_keepalive(data)

        elif packet_id == 0x01:  # Chat preview or disconnect
            # Check if disconnect
            try:
                reason = data.decode('utf-8')
                print(f"[DISCONNECT] {reason}")
                self.running = False
            except:
                pass

        elif packet_id == 0x38:  # Player Info Update
            pass  # Ignore player info

        elif packet_id == 0x3B:  # Synchronize Player Position
            print("[SPAWN] Player position received - ready to play!")

        else:
            print(f"[PACKET 0x{packet_id:02X}] Unhandled, len={len(data)}")

    def handle_system_chat(self, data):
        try:
            offset = 0
            # In 1.19+, System Chat Message has: content (JSON Component), overlay (boolean)
            # content is a Chat Component (NBT format in 1.20.5+)
            # Actually it might be a regular string
            json_len, offset = self.read_varint(data, offset)
            content = data[offset:offset+json_len].decode('utf-8')
            print(f"[CHAT] {content}")
        except Exception as e:
            print(f"[CHAT-PARSE-ERR] {e}, raw: {data[:100].hex()}")

    def handle_keepalive(self, data):
        """Respond to keep alive (varies by version)"""
        print(f"[KEEPALIVE] Sending response")
        self.send_packet(0x12, data)  # Echo back the keep alive ID


def main():
    username = "ArbBot_" + str(int(time.time()) % 100000)
    client = MinecraftClient(HOST, PORT, username)

    # Start connection in a thread
    t = threading.Thread(target=client.connect, daemon=True)
    t.start()

    time.sleep(5)  # Wait for login

    # Send commands
    commands = [
        "/tradebook",
        "/tradebook help",
        "/balance",
        "/help",
    ]

    for cmd in commands:
        time.sleep(2)
        print(f"\n>>> {cmd}")
        try:
            client.send_chat_message(cmd)
        except Exception as e:
            print(f"[!] Send error: {e}")

    time.sleep(10)
    print("\n[DONE]")
    client.running = False

if __name__ == "__main__":
    main()
