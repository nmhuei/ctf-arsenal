"""
Minecraft Protocol Client for 26.1.2 (Protocol 775)
Complete with AuthMe registration + PLAY state interaction
"""
import socket
import struct
import time
import uuid
import zlib
import json
import sys
import threading

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
        self.lock = threading.Lock()
        self.username = "Bot_" + str(int(time.time() % 10000))
        self.my_uuid = uuid.uuid4()
        self.compression = -1
        self.running = True
        self.chat_messages = []
        self.keepalive_id = 0
        self.cmd_index = 0
        self.start_time = time.time()

    def log(self, msg):
        print(msg, flush=True)

    def send_raw(self, raw_data):
        with self.lock:
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

    def send_chat_command(self, command):
        """Send /command via SERVERBOUND_CHAT_COMMAND (0x07)
        In 26.1.2, this packet is just the command string (no timestamp/salt/signature)"""
        data = write_string(command[1:])  # command without /, just a UTF-8 string
        self.send_pkt(0x07, data)

    def send_chat_message(self, message):
        """Send regular chat via SERVERBOUND_CHAT (0x09)"""
        timestamp = int(time.time() * 1000)
        data = (
            write_string(message) +
            struct.pack('>q', timestamp) +
            struct.pack('>q', 0) +
            write_varint(0) +
            write_varint(0) +
            bytes([0])
        )
        self.send_pkt(0x09, data)

    def send_tick_end(self):
        """SERVERBOUND_CLIENT_TICK_END = 0x0D"""
        self.send_pkt(0x0D)
        self.log("  [tick]")

    def send_keepalive_play(self, data):
        self.send_pkt(0x1C, data)
        self.log("  [keepalive]")

    def send_keepalive_config(self, data):
        self.send_pkt(0x04, data)

    def send_pong(self, data):
        self.send_pkt(0x05, data)

    def parse_nbt_chat(self, data, offset=0, anonymous=False):
        """Extract visible text from NBT chat component.
        anonymous=True for root level (no name field) or list elements.
        Only extracts 'text' and 'translate' fields, skipping formatting like color."""
        try:
            if offset >= len(data):
                return '', offset
            tag_type = data[offset]
            offset += 1
            if tag_type == 0:
                return '', offset

            field_name = ''
            if not anonymous:
                if offset + 2 > len(data):
                    return '', offset
                name_len = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                if name_len > 0:
                    field_name = data[offset:offset+name_len].decode('utf-8', errors='replace')
                    offset += name_len
                elif offset + name_len <= len(data):
                    offset += name_len

            if tag_type == 0x08:  # TAG_String
                if offset + 2 > len(data):
                    return '', offset
                val_len = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                if offset + val_len > len(data):
                    val_len = len(data) - offset
                text = data[offset:offset+val_len].decode('utf-8', errors='replace')
                offset += val_len
                # Only return text for meaningful fields (skip color, click_event, etc.)
                if field_name in ('text', 'translate', '') or anonymous:
                    return text, offset
                return '', offset

            elif tag_type == 0x0a:  # TAG_Compound
                text = ''
                while offset < len(data):
                    if data[offset] == 0:  # TAG_End
                        offset += 1
                        break
                    ft, offset = self.parse_nbt_chat(data, offset, anonymous=False)
                    text += ft
                return text, offset

            elif tag_type == 0x09:  # TAG_List
                if offset + 1 > len(data):
                    return '', offset
                list_type = data[offset]
                offset += 1
                if offset + 4 > len(data):
                    return '', offset
                list_len = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                text = ''
                for _ in range(list_len):
                    ft, offset = self.parse_nbt_chat(data, offset, anonymous=True)
                    text += ft
                return text, offset

            return '', offset
        except:
            return '', offset

    def heartbeat_thread(self):
        """Send periodic tick_end and flying packets to stay alive"""
        while self.running:
            time.sleep(0.5)
            if hasattr(self, 'in_play') and self.in_play:
                try:
                    self.send_tick_end()
                except:
                    break

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
            if pid == 0x00:
                reason, _ = self.read_str(payload, 0)
                self.log(f"  DISCONNECT: {reason[:200]}")
                return
            elif pid == 0x02:
                uname, off = self.read_str(payload, 16)
                self.log(f"  LOGIN SUCCESS: {uname}")
                self.send_pkt(0x03)
                login_ok = True
            elif pid == 0x03:
                self.compression, _ = read_varint_data(payload, 0)
                self.log(f"  COMPRESSION: threshold={self.compression}")
            elif pid == 0x04:
                mid, off = read_varint_data(payload, 0)
                ch, off = self.read_str(payload, off)
                self.log(f"  PLUGIN REQ: id={mid}, channel='{ch}'")
                self.send_pkt(0x02, write_varint(mid) + write_varint(0))
            else:
                self.log(f"  UNKNOWN LOGIN 0x{pid:02X}")

        if not self.running:
            return

        # ==================== CONFIGURATION STATE ====================
        self.log("\n--- Configuration State ---")
        self.log("  Sending Client Information (0x00)...")
        info = (
            write_string("en_US") + bytes([12]) + write_varint(0) +
            bytes([1]) + bytes([0x7F]) + write_varint(1) +
            bytes([0]) + bytes([1]) + bytes([0])
        )
        self.send_pkt(0x00, info)

        config_finish = False
        while not config_finish and self.running:
            try:
                pid, payload = self.recv_pkt()
            except (ConnectionError, socket.timeout) as e:
                self.log(f"  [CONFIG END] {e}")
                return
            h = payload[:60].hex()
            if pid == 0x00:
                self.log(f"  [COOKIE REQ]")
            elif pid == 0x01:
                ch, off = self.read_str(payload, 0)
                if ch == "minecraft:brand":
                    blen, boff = read_varint_data(payload, off)
                    brand = payload[boff:boff+blen].decode('utf-8', errors='replace')
                    self.log(f"  [BRAND] {brand}")
                else:
                    self.log(f"  [PLUGIN] {ch}")
            elif pid == 0x02:
                self.log(f"  [DISCONNECT] {h[:50]}")
                return
            elif pid == 0x03:
                self.log(f"  [FINISH CONFIG]")
                config_finish = True
            elif pid == 0x04:
                self.send_keepalive_config(payload)
            elif pid == 0x05:
                self.send_pong(payload)
            elif pid == 0x07:
                pass
            elif pid == 0x0C:
                self.log(f"  [FEATURES]")
            elif pid == 0x0D:
                self.log(f"  [TAGS]")
            elif pid == 0x0E:
                self.log(f"  [KNOWN PACKS]")
                self.send_pkt(0x07, write_varint(0))
            elif pid == 0x11:
                self.log(f"  [CLEAR DIALOG]")
            elif pid == 0x12:
                self.log(f"  [DIALOG] AuthMe registration")
                reg_password = "pw_" + self.username[4:]
                # Build NBT compound: TAG_Compound + TAG_String("password", pwd) + TAG_String("confirm", pwd) + TAG_End
                nbt_password = b'\x08\x00\x08password\x00' + struct.pack('>H', len(reg_password)) + reg_password.encode()
                nbt_confirm = b'\x08\x00\x07confirm\x00' + struct.pack('>H', len(reg_password)) + reg_password.encode()
                nbt = b'\x0a\x00\x00' + nbt_password + nbt_confirm + b'\x00'
                optional = b'\x01' + nbt  # present marker
                click_pkt = write_string("authme:prejoin-register/submit") + write_varint(len(optional)) + optional
                self.send_pkt(0x08, click_pkt)
                self.log(f"  -> registered with pwd={reg_password}")
            elif pid == 0x13:
                self.log(f"  [CODE OF CONDUCT]")
                self.send_pkt(0x09)
            else:
                self.log(f"  [CONFIG 0x{pid:02X}] {h[:30]}")

        if not self.running:
            return

        self.log("--- Sending Finish Config -> PLAY ---")
        self.send_pkt(0x03)
        self.log("--- Now in PLAY state! ---")

        # ==================== PLAY STATE ====================
        self.log("\n--- Play State ---")
        self.sock.settimeout(10)
        self.in_play = True

        # Start heartbeat thread
        hb = threading.Thread(target=self.heartbeat_thread, daemon=True)
        hb.start()

        # Commands to explore
        cmds = [
            "/tradebook",
            "/tradebook help",
            "/tradebook list",
            "/balance",
        ]
        cmd_sent = False
        cmd_timer = time.time()

        while self.running:
            try:
                pid, payload = self.recv_pkt()
            except socket.timeout:
                self.log("  [Timeout]")
                break
            except ConnectionError:
                self.log("  [Disconnected]")
                break

            if pid == 0x18:  # Custom Payload
                ch, off = self.read_str(payload, 0)
                data = payload[off:]
                self.log(f"  [PLUGIN] {ch}")
                if ch == "minecraft:register":
                    channels = data.replace(b'\x00', b', ').decode('utf-8', errors='replace')
                    self.log(f"    channels: {channels}")
            elif pid == 0x20:  # Disconnect
                self.log(f"  [KICK] hex={payload.hex()}")
                break
            elif pid == 0x2C:  # Keep Alive
                self.send_keepalive_play(payload)
            elif pid == 0x31:  # Login/Join
                self.log(f"  [JOIN] World loaded!")
                self.send_pkt(0x2C)  # Player Loaded
                self.send_client_info()
            elif pid == 0x48:  # Player Position
                self.log(f"  [POSITION] Spawned!")
                self.send_pkt(0x00, write_varint(0))  # Accept teleport
            elif pid == 0x61:  # Spawn Position
                self.log(f"  [SPAWN POS]")
            elif pid == 0x76:  # Start Config
                self.log(f"  [START CONFIG]")
                self.in_play = False
                break
            elif pid == 0x79:  # System Chat
                try:
                    text, _ = self.parse_nbt_chat(payload, 0, anonymous=True)
                    if text.strip():
                        self.log(f"  [CHAT] {text[:500]}")
                        self.chat_messages.append(text)
                    else:
                        self.log(f"  [CHAT_EMPTY] raw={payload[:60].hex()}")
                except Exception as e:
                    self.log(f"  [CHAT_ERR] {e} raw={payload[:60].hex()}")
            elif pid == 0x56:  # Server Data
                self.log(f"  [SERVER DATA]")
            elif pid == 0x0B:  # Chunk batch
                pass
            elif pid == 0x0C:
                pass
            elif pid == 0x68:  # Set Health
                pass
            elif pid in (0x5E, 0x5F):  # Chunk cache
                pass
            elif pid == 0x2D:  # Chunk data
                pass
            elif pid == 0x30:  # Light update
                pass
            elif pid == 0x3B:  # Open Screen
                self.log(f"  [OPEN SCREEN]")
            else:
                # Debug: show unknown packets that are not silently consumed above
                # Only log play state packets we haven't handled
                if (pid not in (0x0B, 0x0C, 0x2D, 0x30, 0x5E, 0x5F, 0x68)):
                    h = payload[:40].hex()
                    # Try to decode as string
                    try:
                        txt = payload.decode('utf-8', errors='replace')[:80]
                        self.log(f"  [PKT 0x{pid:02X}] hex={h} str={txt!r}")
                    except:
                        self.log(f"  [PKT 0x{pid:02X}] hex={h}")

            # Send commands after delay
            if not cmd_sent and time.time() - cmd_timer > 5:
                cmd = cmds[self.cmd_index]
                self.log(f"\n>>> / {cmd}")
                self.send_chat_command(cmd)
                self.cmd_index += 1
                cmd_timer = time.time()
                if self.cmd_index >= len(cmds):
                    cmd_sent = True

            if cmd_sent and time.time() - cmd_timer > 10:
                break

        self.log(f"\n=== Messages ({len(self.chat_messages)}) ===")
        for m in self.chat_messages:
            self.log(f"  {m[:300]}")
        self.close()

    def send_client_info(self):
        info = (
            write_string("en_US") + bytes([12]) + write_varint(0) +
            bytes([1]) + bytes([0x7F]) + write_varint(1) +
            bytes([0]) + bytes([1]) + bytes([0])
        )
        self.send_pkt(0x0E, info)

    def close(self):
        self.running = False
        self.in_play = False
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
