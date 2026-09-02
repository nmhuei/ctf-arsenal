"""
Minimal Minecraft Protocol Client v4 - with UUID in Login Start (1.20.5+)
"""
import socket
import struct
import time
import uuid

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
    """Write UUID as 16 bytes: long mostSigBits, long leastSigBits"""
    return struct.pack('>QQ', u.int >> 64, u.int & ((1 << 64) - 1))

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
    data = b''
    while True:
        b = sock.recv(1)
        if not b:
            raise ConnectionError("Closed")
        data += b
        if not (b[0] & 0x80):
            break
    length, _ = read_varint_data(data)
    rest = b''
    while len(rest) < length:
        chunk = sock.recv(length - len(rest))
        if not chunk:
            raise ConnectionError("Closed during data read")
        rest += chunk
    packet_id, offset = read_varint_data(rest)
    payload = rest[offset:]
    return packet_id, payload

# Step 1: Handshake
print("\n=== Handshake (next_state=LOGIN=2) ===")
handshake = write_varint(PROTOCOL_VERSION) + write_string(HOST) + struct.pack('>H', PORT) + write_varint(2)
send_raw(write_varint(0x00) + handshake)

# Step 2: Login Start (1.20.5+ with UUID)
print("\n=== Login Start (with UUID) ===")
my_uuid = uuid.uuid4()
username = "Bot_" + str(int(time.time() % 100000))
print(f"  Username: {username}, UUID: {my_uuid}")
login_start = write_string(username) + write_uuid(my_uuid)
send_raw(write_varint(0x00) + login_start)

# Step 3: Login sequence
print("\n=== Login Sequence ===")
sequence = 0
while sequence < 50:
    try:
        pkt_id, payload = recv_packet()
        print(f"\n[{sequence}] Packet 0x{pkt_id:02X} ({pkt_id}), payload={len(payload)} bytes")
        if len(payload) > 0:
            # Try to decode as JSON
            payload_str = payload.decode('utf-8', errors='replace')
            print(f"     Data: {payload_str[:200]}")
            print(f"     Hex:  {payload[:60].hex()}")

        if pkt_id == 0x02:  # Login Success
            print("     *** LOGIN SUCCESS ***")
        elif pkt_id == 0x03:
            threshold, _ = read_varint_data(payload, 0)
            print(f"     *** SET COMPRESSION threshold={threshold} ***")
        elif pkt_id == 0x04:
            msg_id, off = read_varint_data(payload, 0)
            ch_len, off = read_varint_data(payload, off)
            channel = payload[off:off+ch_len].decode('utf-8', errors='replace')
            print(f"     *** LOGIN PLUGIN REQUEST msg_id={msg_id} channel='{channel}' ***")
            # Respond
            resp = write_varint(msg_id) + write_varint(0)
            send_raw(write_varint(0x02) + resp)
        elif pkt_id in (0x12, 0x21):
            print(f"     *** KEEP ALIVE ***")
            send_raw(write_varint(pkt_id) + payload)
        elif pkt_id == 0x01:
            print("     *** CHAT / DISCONNECT ***")
        elif pkt_id in (0x3B, 0x3C):
            print(f"     *** SPAWN / PLAYER POSITION ***")
        elif pkt_id == 0x5F:
            print(f"     *** SYSTEM CHAT ***")
        elif pkt_id == 0x0C:
            print("     *** SERVERBOUND LOGIN ACKNOWLEDGED? ***")
        elif pkt_id == 0x23:
            print("     *** CONFIG DISCONNECT? ***")

        sequence += 1
    except socket.timeout:
        print(f"\n[{sequence}] Timeout")
        break
    except ConnectionError:
        print(f"\n[{sequence}] Connection closed")
        break
    except Exception as e:
        print(f"\n[{sequence}] Error: {e}")
        import traceback
        traceback.print_exc()
        break

print(f"\n=== Done ({sequence} packets) ===")
sock.close()
