"""
Minimal Minecraft Protocol Client v2 - more debugging
"""
import socket
import struct
import time
import sys

HOST = "skyblock.chals.sekai.team"
PORT = 25565
PROTOCOL_VERSION = 775  # Minecraft 26.1.2

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

def read_varint(data, offset=0):
    result = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of varint at offset %d" % offset)
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

def send_packet(sock, packet_id, data=b'', compression=-1):
    raw = write_varint(packet_id) + data
    if compression >= 0:
        if len(raw) >= compression:
            import zlib
            compressed = zlib.compress(raw)
            full_data = write_varint(len(raw)) + compressed
        else:
            full_data = write_varint(0) + raw
        size_data = write_varint(len(full_data)) + full_data
    else:
        size_data = write_varint(len(raw)) + raw
    print(f"  [SEND] Packet 0x{packet_id:02X}, raw_len={len(raw)}, total_len={len(size_data)}")
    sock.sendall(size_data)

def read_fully(sock, length):
    result = bytearray()
    while len(result) < length:
        chunk = sock.recv(length - len(result))
        if not chunk:
            raise ConnectionError("Connection closed")
        result.extend(chunk)
    return bytes(result)

# Step 1: Handshake -> LOGIN state
print("\n--- Handshake ---")
raw = write_varint(PROTOCOL_VERSION) + write_string(HOST) + struct.pack('>H', PORT) + write_varint(2)
send_packet(sock, 0x00, raw)

# Step 2: Login Start
print("\n--- Login Start ---")
send_packet(sock, 0x00, write_string("ArbBot_" + str(int(time.time()) % 10000)))

# Step 3: Read packets
compression = -1
print("\n--- Reading packets ---")
for i in range(20):
    try:
        # Read packet length
        first_byte = sock.recv(1)
        if not first_byte:
            print("Connection closed")
            break
        length, _ = read_varint(first_byte)
        # Read rest of length if needed
        remaining = length - 1
        while remaining > 0:
            chunk = sock.recv(remaining)
            if not chunk:
                break
            first_byte += chunk
            remaining -= len(chunk)
        # Now first_byte = full length varint + data
        actual = len(first_byte) - 1 - remaining  # wait, let me redo

        # Actually, let's re-read properly
        pass
    except socket.timeout:
        print(f"[{i}] Timeout waiting for packet")
        break
    except Exception as e:
        print(f"[{i}] Error: {e}")
        break

# Let me redo with proper reading
sock.close()
print("\nDone")
