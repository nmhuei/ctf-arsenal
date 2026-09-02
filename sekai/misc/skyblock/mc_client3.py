"""
Minimal Minecraft Protocol Client - Step by step debug
"""
import socket
import struct
import time

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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
print("Connecting...")
sock.connect((HOST, PORT))
print("Connected!")

def send_raw(raw_data):
    """Send a Minecraft packet: length-varint + raw_data"""
    sock.sendall(write_varint(len(raw_data)) + raw_data)
    print(f"  Sent {len(raw_data)} bytes: {raw_data[:40].hex() + ('...' if len(raw_data)>40 else '')}")

def recv_packet():
    """Receive one Minecraft packet, raises on timeout"""
    # Read varint packet length
    data = b''
    while True:
        b = sock.recv(1)
        if not b:
            raise ConnectionError("Closed")
        data += b
        if not (b[0] & 0x80):
            break
    length, _ = read_varint_data(data)
    # Read the rest
    rest = b''
    while len(rest) < length:
        chunk = sock.recv(length - len(rest))
        if not chunk:
            raise ConnectionError("Closed during data read")
        rest += chunk
    print(f"  Received packet: length={length}, total_data_len={len(rest)}")
    # Parse packet ID
    packet_id, offset = read_varint_data(rest)
    payload = rest[offset:]
    return packet_id, payload

# Step 1: Handshake
print("\n=== Handshake (next_state=LOGIN=2) ===")
handshake = write_varint(PROTOCOL_VERSION) + write_string(HOST) + struct.pack('>H', PORT) + write_varint(2)
send_raw(write_varint(0x00) + handshake)

# Step 2: Login Start
print("\n=== Login Start ===")
username = "Bot_" + str(int(time.time() % 100000))
login_start = write_string(username)
send_raw(write_varint(0x00) + login_start)

# Step 3: Login sequence
print("\n=== Login Sequence ===")
sequence = 0
while sequence < 30:
    try:
        pkt_id, payload = recv_packet()
        print(f"[{sequence}] Packet 0x{pkt_id:02X} ({pkt_id}), payload={len(payload)} bytes")
        print(f"     Payload hex: {payload[:80].hex()}")
        if len(payload) > 0:
            print(f"     Payload str: {payload[:80]}")

        if pkt_id == 0x02:  # Login Success (1.20+?)
            print("     -> LOGIN SUCCESS")
            # Attempt to parse UUID and username
            try:
                u1, off = read_varint_data(payload, 0)
                # Actually in newer versions, UUID might be an int array
                # Let me skip complex parsing for now
            except:
                pass
        elif pkt_id == 0x03:
            threshold, _ = read_varint_data(payload, 0)
            print(f"     -> SET COMPRESSION threshold={threshold}")
        elif pkt_id == 0x04:
            msg_id, off = read_varint_data(payload, 0)
            ch_len, off = read_varint_data(payload, off)
            channel = payload[off:off+ch_len].decode('utf-8', errors='replace')
            print(f"     -> LOGIN PLUGIN REQUEST msg_id={msg_id} channel='{channel}'")
            # Send response
            resp = write_varint(msg_id) + write_varint(0)
            send_raw(write_varint(0x02) + resp)
        elif pkt_id == 0x00:
            print("     -> CONFIGURATION/PLAY packet?")
        elif pkt_id in (0x21, 0x12):  # Keep Alive (different versions)
            print(f"     -> KEEP ALIVE, echoing back")
            send_raw(write_varint(pkt_id) + payload)
        elif pkt_id == 0x01:
            reason = payload.decode('utf-8', errors='replace')
            print(f"     -> CHAT / DISCONNECT: {reason}")
        elif pkt_id == 0x5F:
            # System Chat Message
            print(f"     -> SYSTEM CHAT")
        elif pkt_id == 0x0C:
            print("     -> LOGIN ACKNOWLEDGED (from server?)")
        elif pkt_id == 0x03 and sequence == 0:
            # Could be different if first packet
            pass

        sequence += 1
    except socket.timeout:
        print(f"[{sequence}] Timeout - no more packets")
        break
    except Exception as e:
        print(f"[{sequence}] Error: {e}")
        import traceback
        traceback.print_exc()
        break

print("\n=== Done ===")
sock.close()
