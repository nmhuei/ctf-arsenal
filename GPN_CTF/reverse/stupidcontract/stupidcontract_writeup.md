# stupidcontract — CTF Writeup

## Result

- **Flag**: `GPNCTF{WA17, N0! Who sto13 my 53Cur1ty???}`
- **Category**: Reverse Engineering
- **Server**: `ncat --ssl charred-crab-over-braised-harissa-83m8.gpn24.ctf.kitctf.de 443`

## Tổng quan challenge

Challenge cung cấp một archive chứa:

```text
stupidcontract/
├── Dockerfile
├── compose.yml
├── flag                          # dummy flag local
├── images/
│   ├── patched.bzImage           # kernel đã patch
│   └── unpatched.bzImage
├── rootfs.ext2                   # root filesystem (ext2)
└── run-qemu.sh                   # script khởi động QEMU
```

`run-qemu.sh` khởi động QEMU với `patched.bzImage`, mount `rootfs.ext2` làm root, và share thư mục `/flag-data` vào guest qua 9p. Bên trong guest, init script mount 9p vào `/tmp/flag-data`, và binary challenge đọc flag từ `/tmp/flag-data/flag` khi exploit thành công.

`Dockerfile` cho thấy server dùng `socat` để listen trên port 1337, forward mỗi connection vào một QEMU instance mới.

## Phân tích tĩnh

### Binary chính

Dùng `debugfs` để extract binary từ rootfs:

```bash
debugfs -R "dump /usr/bin/stupidcontract stupidcontract_bin" rootfs.ext2
```

Binary là một Rust ELF (`not stripped`), chứa một eBPF object được nhúng tại offset `0x2c468`, kích thước `0x1610` bytes.

```bash
dd if=stupidcontract_bin of=ebpf.o bs=1 skip=$((0x2c468)) count=$((0x1610))
```

### eBPF object

eBPF object gồm các section và symbol quan trọng:

| Section | Size | Mô tả |
|---------|------|--------|
| `syscall` | 0xce8 | Chứa 2 function: `try_get_reservation` và `validate_reservations` |
| `.bss` | 0x65 (101 bytes) | Mảng `DATA[101]` — state lưu kết quả reservation |
| `maps` | 0x1c | Map definition cho BPF |

Symbols:

| Symbol | Offset | Size | Mô tả |
|--------|--------|------|--------|
| `try_get_reservation` | 0x000 | 3112 | Xử lý mỗi lần user chọn restaurant |
| `validate_reservations` | 0xc28 | 192 | Kiểm tra tất cả restaurant đã reserved chưa |
| `DATA` (`.bss`) | 0x000 | 101 | `DATA[0]` = success flag, `DATA[1..100]` = trạng thái 100 restaurant |

## Phân tích eBPF chi tiết

### `try_get_reservation` — Logic chính

Disassemble bằng `llvm-objdump-18`:

```asm
; r1 = pointer to user input struct
; r7 = user_index (64-bit signed)
       3:  r7 = *(u64 *)(r1 + 0x0)         ; đọc index từ input
       4:  if r7 s> 0x63 goto +0xd          ; CHỈ CHECK UPPER BOUND (signed)!
                                             ; nếu index > 99 → jump tới log/reject
; === Nếu index <= 99 (signed), tiếp tục ===
       5:  call 0x7                          ; bpf_get_prng_u32() — random 32-bit
       6:  r1 = r0
       7:  r1 <<= 0x20                      ; clear upper 32 bits
       8:  r1 >>= 0x20                      ; r1 = lower 32 bits of random
       9:  r0 = 0x1                          ; giả sử success
      10:  r2 = 0x33333333                   ; threshold ≈ 20%
      11:  if r2 > r1 goto +0x1              ; nếu random < threshold → giữ r0=1
      12:  r0 = 0x0                          ; ngược lại → r0=0 (fail)

      13:  r1 = <.bss>                       ; r1 = &DATA (relocation tới .bss)
      15:  r1 += r7                          ; r1 = &DATA + index
      16:  *(u8 *)(r1 + 0x1) = r0            ; DATA[index + 1] = r0
```

### Lỗ hổng: Thiếu kiểm tra lower bound

Dòng 4 chỉ check `if r7 s> 0x63` (signed greater than 99). **Không có kiểm tra lower bound!**

Mọi giá trị âm đều pass check này vì `-1 s> 99` là **false**.

Khi `index = -1`:

```
DATA[index + 1] = DATA[-1 + 1] = DATA[0]
```

`DATA[0]` chính là **byte quyết định thành công** — byte mà `validate_reservations` set khi tất cả restaurant đã reserved.

### `validate_reservations` — Kiểm tra cuối cùng

```asm
      389:  r2 = 0x1                  ; accumulator = 1 (true)
      390:  r1 = 0x1                  ; index = 1
      391:  goto loop_body

 set_false:
      392:  r2 = 0x0                  ; accumulator = 0

 check_done:
      393:  if r1 == 0x64 goto final  ; nếu index == 100 → kiểm tra kết quả
      394:  r1 += 0x1                 ; index++
      395:  r2 &= 0x1
      396:  if r2 != 0x0 goto read    ; nếu accumulator vẫn true → đọc tiếp
      397:  goto set_false            ; đã false → skip đọc, giữ false

 read:
      398:  r2 = <.bss>              ; r2 = &DATA
      400:  r2 += r1                  ; r2 = &DATA[index]
      401:  r2 = *(u8 *)(r2 + 0x0)   ; r2 = DATA[index]
      402:  if r1 == 0x64 goto final
      403:  goto check_done

 final:
      404:  r2 &= 0x1
      405:  if r2 != 0x0 goto success ; nếu tất cả != 0 → set DATA[0]=1
      406:  goto exit                 ; KHÔNG clear DATA[0] nếu fail!

 success:
      407:  r1 = <.bss>              ; r1 = &DATA
      409:  r2 = 0x1
      410:  *(u8 *)(r1 + 0x0) = r2   ; DATA[0] = 1

 exit:
      411:  r0 = 0x0
      412:  exit
```

**Điểm quan trọng**: Nếu validation fail (không đủ 100 restaurant), hàm **KHÔNG clear `DATA[0]`** về 0. Nó chỉ nhảy thẳng tới exit.

### Rust binary — Đọc kết quả

Từ strings trong binary:

```
SUCCESS map not found
Could not get success status
Sorry, I cannot give you a flag. You did not get reservations to all restaurants
Thank you! You successfully got reservations to every restaurant
```

Flow:
1. Chạy 300 lần `try_get_reservation` với input từ user
2. Gọi `validate_reservations`
3. Đọc `DATA[0]` — nếu = 1 → in flag, nếu = 0 → in lỗi

## Exploit

### Ý tưởng

1. Gửi index `-1` cho tất cả 300 lần
2. Mỗi lần ghi `DATA[0]` = kết quả random (1 với xác suất ~20%, 0 với ~80%)
3. Sau 300 lần, `DATA[0]` = giá trị từ lần ghi **cuối cùng**
4. `validate_reservations` chạy: vì không restaurant nào được reserved, nó **KHÔNG set** `DATA[0]` = 1, nhưng cũng **KHÔNG clear** nó
5. Nếu lần cuối may mắn ghi 1 → `DATA[0]` = 1 → flag!

**Xác suất thành công mỗi connection**: ~20%

**Chiến thuật**: Retry nhiều connection. Với 6 lần thử → xác suất ≈ 1 - 0.8⁶ ≈ 74%.

### Lưu ý quan trọng: VM boot time

Server chạy QEMU — mỗi connection tạo một VM mới. VM cần **30-60 giây** để boot. Solver phải **đợi prompt xuất hiện** trước khi gửi input, nếu không data sẽ bị mất.

### Solver script

```python
#!/usr/bin/env python3
# solve_remote.py - Kết nối SSL, đợi VM boot, gửi -1 x300, retry

import re, socket, ssl, sys, time

HOST = "charred-crab-over-braised-harissa-83m8.gpn24.ctf.kitctf.de"
PORT = 443
FLAG_RE = re.compile(rb"GPNCTF\{[^\}\r\n]+\}")
PROMPT_RE = re.compile(rb"For which restaurant do you want a reservation")

def connect():
    raw = socket.create_connection((HOST, PORT), timeout=30)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx.wrap_socket(raw, server_hostname=HOST)

def recv_until(sock, pattern, timeout):
    end = time.time() + timeout
    data = bytearray()
    sock.setblocking(False)
    try:
        while time.time() < end:
            try:
                chunk = sock.recv(8192)
                if chunk:
                    data += chunk
                    if pattern.search(data): return bytes(data), True
                else: break
            except (BlockingIOError, ssl.SSLWantReadError):
                time.sleep(0.05)
    finally:
        sock.setblocking(True)
    return bytes(data), False

for attempt in range(1, 16):
    s = connect()
    data, found = recv_until(s, PROMPT_RE, 120)  # đợi VM boot
    if not found: continue

    all_data = bytearray(data)
    for i in range(300):
        s.sendall(b"-1\n")
        resp, _ = recv_until(s, PROMPT_RE, 5 if i < 299 else 30)
        all_data += resp
        m = FLAG_RE.search(all_data)
        if m:
            print(m.group(0).decode())
            sys.exit(0)
    s.close()
    time.sleep(5)
```

### Kết quả

```
[*] Connection attempt 1 → No luck
[*] Connection attempt 2 → No luck
[*] Connection attempt 3 → No luck
[*] Connection attempt 4 → No luck
[*] Connection attempt 5 → No luck
[*] Connection attempt 6 → FLAG FOUND!

GPNCTF{WA17, N0! Who sto13 my 53Cur1ty???}
```

## Tóm tắt

```text
Bug:     Signed-only upper bound check (if r7 s> 99) → thiếu lower bound
Input:   index = -1 → ghi vào DATA[0] thay vì DATA[1..100]
Effect:  DATA[0] (success byte) bị ghi trực tiếp, bypass validate_reservations
Caveat:  Random gate 20% → cần retry connections
Flag:    GPNCTF{WA17, N0! Who sto13 my 53Cur1ty???}
```
