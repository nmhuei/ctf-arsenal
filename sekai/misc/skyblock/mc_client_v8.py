"""
Minecraft Protocol Client for 26.1.2 (Protocol 775)
Correct packet IDs extracted from decompiled client JAR
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
                raise ConnectionError("Closed during read")
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

    def send_chat_play(self, message):
        """SERVERBOUND_CHAT = 0x09 for messages, SERVERBOUND_CHAT_COMMAND = 0x07 for /commands"""
        timestamp = int(time.time() * 1000)
        if message.startswith('/'):
            # Use SERVERBOUND_CHAT_COMMAND (0x07)
            # Format: command (String), timestamp (Long), salt (Long),
            #         argumentSignatures (VarInt count + ...), messageCount (VarInt), acknowledged (BitSet)
            data = (
                write_string(message[1:]) +  # command without /
                struct.pack('>q', timestamp) +
                struct.pack('>q', 0) +
                write_varint(0) +  # argument signatures count
                write_varint(0) +  # message count
                bytes([0])           # acknowledged bits
            )
            self.send_pkt(0x07, data)
        else:
            # SERVERBOUND_CHAT (0x09)
            data = (
                write_string(message) +
                struct.pack('>q', timestamp) +
                struct.pack('>q', 0) +
                write_varint(0) +  # signature length = 0 (unsigned)
                write_varint(0) +  # message count = 0
                bytes([0])
            )
            self.send_pkt(0x09, data)

    def send_client_info(self):
        """SERVERBOUND_CLIENT_INFORMATION = 0x0E"""
        info = (
            write_string("en_US") +
            bytes([12]) +          # view-distance
            write_varint(0) +      # chat-mode: enabled
            bytes([1]) +           # chat-colors: true
            bytes([0x7F]) +        # skin-parts: all
            write_varint(1) +      # main-hand: right
            bytes([0]) +           # text-filtering: disabled
            bytes([1]) +           # server-listing: enabled
            bytes([0])             # particle-status: all
        )
        self.send_pkt(0x0E, info)

    def send_keepalive_play(self, data):
        """SERVERBOUND_KEEP_ALIVE = 0x1C"""
        self.send_pkt(0x1C, data)

    def send_keepalive_config(self, data):
        """SERVERBOUND_KEEP_ALIVE in CONFIG = 0x04"""
        self.send_pkt(0x04, data)

    def send_pong(self, data):
        """SERVERBOUND_PONG = 0x05"""
        self.send_pkt(0x05, data)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.log("Connecting...")
        self.sock.connect((self.host, self.port))
        self.log(f"Connected as {self.username} / {self.my_uuid}")

        # ==================== HANDSHAKE ====================
        self.log("\n--- Handshake -> LOGIN ---")
        hs = write_varint(PROTOCOL_VERSION) + write_string(self.host) + struct.pack('>H', self.port) + write_varint(2)
        self.send_pkt(0x00, hs)

        # ==================== LOGIN START ====================
        self.log("--- Login Start ---")
        ls = write_string(self.username) + write_uuid(self.my_uuid)
        self.send_pkt(0x00, ls)

        # ==================== LOGIN STATE ====================
        self.log("--- Login State ---")
        login_ok = False
        while not login_ok and self.running:
            pid, payload = self.recv_pkt()
            if pid == 0x00:  # Login Disconnect
                reason, _ = self.read_str(payload, 0)
                self.log(f"  DISCONNECT: {reason[:200]}")
                return
            elif pid == 0x02:  # Login Success
                server_uuid = uuid.UUID(bytes=payload[:16])
                uname, off = self.read_str(payload, 16)
                self.log(f"  LOGIN SUCCESS: {uname} ({server_uuid})")
                self.log("  Sending Login Acknowledged (0x03)...")
                self.send_pkt(0x03)
                login_ok = True
            elif pid == 0x03:  # Set Compression
                self.compression, _ = read_varint_data(payload, 0)
                self.log(f"  COMPRESSION: threshold={self.compression}")
            elif pid == 0x04:  # Login Plugin Request
                mid, off = read_varint_data(payload, 0)
                ch, off = self.read_str(payload, off)
                self.log(f"  PLUGIN REQ: id={mid}, channel='{ch}'")
                self.send_pkt(0x02, write_varint(mid) + write_varint(0))
            elif pid == 0x01:
                self.log(f"  UNKNOWN LOGIN 0x01")
            else:
                self.log(f"  UNKNOWN LOGIN 0x{pid:02X}: {payload[:40].hex()}")

        if not self.running:
            return

        # ==================== CONFIGURATION STATE ====================
        # Correct packet IDs for protocol 775:
        # Serverbound: CLIENT_INFO=0x00, KEEPALIVE=0x04, PONG=0x05, SELECT_KNOWN_PACKS=0x07, FINISH_CONFIG=0x03
        # Clientbound: COOKIE_REQ=0x00, PLUGIN_MSG=0x01, DISCONNECT=0x02, FINISH_CONFIG=0x03,
        #              KEEPALIVE=0x04, PING=0x05, REGISTRY=0x07, FEATURES=0x0C, TAGS=0x0D,
        #              SELECT_KNOWN_PACKS=0x0E, CODE_OF_CONDUCT=0x13

        self.log("\n--- Configuration State ---")

        # Send client info FIRST (required)
        self.log("  Sending Client Information (0x00)...")
        info = (
            write_string("en_US") + bytes([12]) + write_varint(0) +
            bytes([1]) + bytes([0x7F]) + write_varint(1) +
            bytes([0]) + bytes([1]) + bytes([0])
        )
        self.send_pkt(0x00, info)
        self.log("  Client info sent")

        config_finish = False
        while not config_finish and self.running:
            try:
                pid, payload = self.recv_pkt()
            except ConnectionError:
                self.log("  [Connection lost]")
                return
            except socket.timeout:
                self.log("  [Timeout]")
                break

            h = payload[:60].hex()

            if pid == 0x00:  # Cookie Request (ignore)
                self.log(f"  [COOKIE REQ]")
            elif pid == 0x01:  # Custom Payload (Plugin Message)
                ch, off = self.read_str(payload, 0)
                if ch == "minecraft:brand":
                    blen, boff = read_varint_data(payload, off)
                    brand = payload[boff:boff+blen].decode('utf-8', errors='replace')
                    self.log(f"  [BRAND] {brand}")
                else:
                    self.log(f"  [PLUGIN] {ch}")
            elif pid == 0x02:  # Disconnect
                reason, _ = self.read_str(payload, 0)
                self.log(f"  DISCONNECT: {reason[:200]}")
                return
            elif pid == 0x03:  # Finish Configuration
                self.log(f"  [FINISH CONFIG] Server ready!")
                config_finish = True
            elif pid == 0x04:  # Keep Alive
                self.send_keepalive_config(payload)
                self.log(f"  [KEEPALIVE]")
            elif pid == 0x05:  # Ping
                self.send_pong(payload)
                self.log(f"  [PING]")
            elif pid == 0x07:  # Registry Data
                pass
            elif pid == 0x0C:  # Update Enabled Features
                self.log(f"  [FEATURES] {h[:30]}")
            elif pid == 0x0D:  # Update Tags
                self.log(f"  [TAGS]")
            elif pid == 0x0E:  # Select Known Packs
                self.log(f"  [KNOWN PACKS]")
                # Respond with 0x07 (SERVERBOUND_SELECT_KNOWN_PACKS)
                self.send_pkt(0x07, write_varint(0))
                self.log(f"  -> sent response (empty)")
            elif pid == 0x11:  # Clear Dialog
                self.log(f"  [CLEAR DIALOG]")
            elif pid == 0x12:  # Show Dialog
                self.log(f"  [SHOW DIALOG] len={len(payload)}")
                # This is an AuthMe registration dialog with:
                # - Type: minecraft:multi_action
                # - Title: "Register"
                # - Buttons: submit (authme:prejoin-register/submit) and cancel (authme:prejoin-register/cancel)
                # - Inputs: password + confirm
                # Send CUSTOM_CLICK_ACTION with submit action and NBT payload
                reg_password = "pwd_" + self.username[4:]
                # Build CompoundTag: {password: "xxx", confirm: "xxx"}
                # TAG_Compound{name=""} + TAG_String(name="password", val=pass) + TAG_String(name="confirm", val=pass) + TAG_End
                def write_nbt_string(name, value):
                    name_bytes = name.encode('utf-8')
                    val_bytes = value.encode('utf-8')
                    return b'\x08' + struct.pack('>H', len(name_bytes)) + name_bytes + struct.pack('>H', len(val_bytes)) + val_bytes
                nbt = b'\x0a\x00\x00'  # TAG_Compound, empty name
                nbt += write_nbt_string("password", reg_password)
                nbt += write_nbt_string("confirm", reg_password)
                nbt += b'\x00'  # TAG_End
                # Optional<CompoundTag>: byte 1 (present) + NBT data
                # Then length prefix wrapping the whole optional
                optional_data = b'\x01' + nbt
                submit_pkt = write_string("authme:prejoin-register/submit") + write_varint(len(optional_data)) + optional_data
                self.send_pkt(0x08, submit_pkt)
                self.log(f"  -> registered with password={reg_password}")
            elif pid == 0x13:  # Code of Conduct
                self.log(f"  [CODE OF CONDUCT]")
                self.send_pkt(0x09)  # empty payload
                self.log(f"  -> accepted")
            else:
                self.log(f"  [CONFIG 0x{pid:02X}] {h[:40]}")

        if not self.running:
            return

        # Send Finish Configuration -> PLAY
        self.log("\n--- Sending Finish Configuration (0x03) -> PLAY ---")
        self.send_pkt(0x03)
        self.log("--- Now in PLAY state! ---")

        # ==================== PLAY STATE ====================
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
        player_loaded = False

        while self.running:
            try:
                pid, payload = self.recv_pkt()
            except socket.timeout:
                self.log("\n  [Timeout]")
                break
            except ConnectionError:
                self.log("\n  [Disconnected]")
                break

            # Correct PLAY clientbound packet IDs for 26.1.2:
            if pid == 0x18:  # Custom Payload
                ch, off = self.read_str(payload, 0)
                self.log(f"  [PLUGIN] {ch}")
            elif pid == 0x20:  # Disconnect (Kick)
                reason, _ = self.read_str(payload, 0)
                self.log(f"  [KICK] {reason[:300]}")
                break
            elif pid == 0x2C:  # Keep Alive -> echo back with 0x1C
                self.send_keepalive_play(payload)
            elif pid == 0x31:  # Login (world join)
                self.log(f"  [JOIN] World loaded!")
                if not player_loaded:
                    self.log("  Sending Player Loaded (0x2C)...")
                    self.send_pkt(0x2C)
                    self.log("  Sending Client Info (0x0E)...")
                    self.send_client_info()
                    player_loaded = True
            elif pid == 0x48:  # Player Position
                self.log(f"  [POSITION] Spawned!")
                self.send_pkt(0x00, write_varint(0))  # Accept teleport
            elif pid == 0x61:  # Default Spawn Position
                self.log(f"  [SPAWN POS] Set")
            elif pid == 0x76:  # Start Configuration
                self.log(f"  [START CONFIG] Back to config")
                break
            elif pid == 0x79:  # System Chat (SYSTEM_CHAT = 0x79)
                try:
                    # In 26.1.2, system chat uses NBT chat component + boolean overlay
                    # Parse NBT component to extract text
                    def parse_nbt_text(data, offset=0):
                        """Extract text from NBT chat component"""
                        if offset >= len(data):
                            return '', offset
                        tag_type = data[offset]
                        offset += 1
                        if tag_type == 0:  # TAG_End
                            return '', offset
                        # Read name length (2 bytes big-endian)
                        if offset + 2 > len(data):
                            return '', offset
                        name_len = struct.unpack('>H', data[offset:offset+2])[0]
                        offset += 2
                        name = data[offset:offset+name_len].decode('utf-8', errors='replace') if name_len > 0 else ''
                        offset += name_len
                        if tag_type == 0x08:  # TAG_String
                            val_len = struct.unpack('>H', data[offset:offset+2])[0]
                            offset += 2
                            text = data[offset:offset+val_len].decode('utf-8', errors='replace')
                            offset += val_len
                            return text, offset
                        elif tag_type == 0x0a:  # TAG_Compound
                            text = ''
                            while offset < len(data):
                                if data[offset] == 0:  # TAG_End
                                    offset += 1
                                    break
                                field_text, offset = parse_nbt_text(data, offset)
                                text += field_text
                            return text, offset
                        elif tag_type == 0x09:  # TAG_List
                            list_type = data[offset]
                            offset += 1
                            list_len = struct.unpack('>I', data[offset:offset+4])[0]
                            offset += 4
                            text = ''
                            for _ in range(list_len):
                                item_text, offset = parse_nbt_text(data, offset)
                                text += item_text
                            return text, offset
                        else:
                            return '', offset

                    nbt_text, _ = parse_nbt_text(payload, 0)
                    if nbt_text.strip():
                        self.log(f"  [CHAT] {nbt_text[:500]}")
                        self.chat_messages.append(nbt_text)
                    else:
                        self.log(f"  [CHAT] (empty/formatting)")
                except Exception as e:
                    self.log(f"  [CHAT] parse error: {e}")
            elif pid == 0x56:  # Server Data (server info)
                self.log(f"  [SERVER DATA]")
            elif pid == 0x6F:  # Simulation Distance
                pass
            elif pid == 0x2D:  # Chunk data (LEVEL_CHUNK_WITH_LIGHT)
                pass
            elif pid == 0x30:  # Light Update
                pass
            elif pid == 0x5E:  # Chunk Cache Center
                pass
            elif pid == 0x5F:  # Chunk Cache Radius
                pass
            elif pid == 0x68:  # Set Health
                pass
            elif pid == 0x3B:  # Open Screen
                self.log(f"  [OPEN SCREEN]")
            elif pid >= 0x80:
                pass  # Unknown/high ID packets, ignore
            else:
                pass  # Silently ignore other packets

            # Send commands
            if cmd_idx < len(cmds) and time.time() - cmd_timer > 3:
                cmd = cmds[cmd_idx]
                self.log(f"\n>>> / {cmd}")
                self.send_chat_play(cmd)
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
