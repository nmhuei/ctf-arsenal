# Writeup — koenigsberg-delivery-problem

## 1. Thông tin bài

Challenge cung cấp một file nén:

```bash
koenigsberg-delivery-problem.tar(1).gz
```

Sau khi giải nén có binary chính:

```bash
cartographer
```

Kiểm tra nhanh:

```bash
file cartographer
```

Kết quả quan trọng:

```text
ELF 64-bit LSB pie executable, x86-64, not stripped
```

Điểm thuận lợi là binary **not stripped**, nên các symbol như `main`, `cfg`, `check_instance` vẫn còn. Điều này giúp reverse nhanh hơn rất nhiều.

---

## 2. Ý tưởng tổng quát

Tên bài là **Königsberg delivery problem**, gợi ý đến bài toán đi qua các cạnh/đỉnh trong đồ thị.

Sau khi reverse, bài thực chất là một bài **đồ thị hữu hạn có 250 trạng thái**:

- Chương trình đọc đúng **250 số nguyên byte** từ input.
- Mỗi số là một “lệnh đi đường”.
- Hàm `cfg()` mô phỏng việc di chuyển giữa các state.
- Mỗi khi ghé vào một state, chương trình tăng counter của state đó.
- Muốn lấy flag thì phải làm cho **tất cả 250 counter đều khác 0**, tức là phải đi qua đủ 250 state.
- Sau khi đi đủ 250 state, gửi một lệnh không hợp lệ để chương trình rơi vào `check_instance()`.

Nói ngắn gọn: cần tìm một đường đi bắt đầu từ state 0, đi qua đủ 250 state, rồi kết thúc bằng transition invalid.

---

## 3. Phân tích `main()`

Disassemble binary:

```bash
objdump -d -M intel ./cartographer > disasm.txt
```

Trong `main()`, chương trình gọi `scanf` rất nhiều lần. Format string là:

```text
%hhd;
```

Có tổng cộng 250 lần đọc, tương đương dạng input:

```text
39;11;35;62;...;127;
```

Mỗi số được đọc vào một byte. Sau khi đọc xong, chương trình gọi:

```asm
call cfg
```

Pseudo-code đơn giản của `main()`:

```c
int main() {
    char input[250];

    for (int i = 0; i < 250; i++) {
        scanf("%hhd;", &input[i]);
    }

    cfg(input);
    return 0;
}
```

Điểm quan trọng: input không phải string flag, mà là **250 số cách nhau bằng dấu `;`**.

---

## 4. Phân tích `check_instance()`

Trong binary có hàm `check_instance` tại địa chỉ khoảng `0x5520`.

Đoạn logic chính:

```asm
cmp BYTE PTR [rdi+rsi*1],0x0
cmove ecx,edx
...
test cl,0x1
je fail
```

Hàm này nhận vào:

```c
check_instance(counters, 250)
```

Nó kiểm tra toàn bộ 250 byte counter. Nếu có bất kỳ counter nào bằng 0, chương trình in:

```text
Not quite, try again!
```

Nếu toàn bộ counter đều khác 0, chương trình mở file `/flag` và in:

```text
Congratulations! Here is your flag: <flag>
```

Pseudo-code:

```c
void check_instance(uint8_t *cnt, int n) {
    int ok = 1;

    for (int i = 0; i < n; i++) {
        if (cnt[i] == 0) {
            ok = 0;
        }
    }

    if (!ok) {
        puts("Not quite, try again!");
        exit(0);
    }

    fd = open("/flag", 0);
    read(fd, buf, 100);
    printf("Congratulations! Here is your flag: %s", buf);
    exit(0);
}
```

Vậy điều kiện lấy flag là:

```text
cnt[0] != 0
cnt[1] != 0
...
cnt[249] != 0
```

Tức là phải ghé qua đủ 250 state.

---

## 5. Phân tích `cfg()`

Hàm `cfg()` là phần chính của challenge.

Ở đầu hàm, chương trình tạo vùng counter 250 byte trên stack và set toàn bộ về 0:

```asm
sub rsp,0x108
xorps xmm0,xmm0
movaps ...
```

Sau đó bắt đầu ở state 0:

```asm
inc BYTE PTR [rsp]
movzx edx,BYTE PTR [rdi+rcx*1]
cmp rdx,0x5f
ja check
inc rcx
movsxd rdx,DWORD PTR [rax+rdx*4]
add rdx,rax
jmp rdx
```

Có thể hiểu state 0 như sau:

```c
state_0:
    cnt[0]++;
    x = input[pos];

    if (x > max_allowed_for_state_0) {
        goto finish;
    }

    pos++;
    goto jump_table_0[x];
```

Các state khác cũng tương tự:

```asm
inc BYTE PTR [rsp+state_id]
movzx edx,BYTE PTR [rdi+rcx*1]
cmp rdx, max_value
ja finish
inc rcx
lea rsi, [jump_table]
movsxd rdx, DWORD PTR [rsi+rdx*4]
add rdx, rsi
jmp rdx
```

Điểm cực kỳ quan trọng:

```asm
ja 40d4
...
40d4:
    mov rdi,rsp
    mov esi,0xfa
    call check_instance
```

Nếu nhập một số không hợp lệ tại state hiện tại, chương trình **không chết ngay**, mà gọi `check_instance()`.

Vì vậy chiến thuật là:

1. Đi qua đủ 250 state bằng 249 transition hợp lệ.
2. Ở state cuối cùng, gửi một số invalid.
3. Invalid transition sẽ gọi `check_instance()`.
4. Vì đã đi qua đủ state, tất cả counter khác 0, chương trình in flag.

---

## 6. Mô hình hóa thành đồ thị

Mỗi state là một node.

Mỗi input byte hợp lệ là một cạnh có nhãn:

```text
state hiện tại --input_byte--> state tiếp theo
```

Ví dụ nếu ở state 0, input `39` làm nhảy sang state khác, ta có cạnh:

```text
0 --39--> next_state
```

Bài toán trở thành:

```text
Tìm một đường đi bắt đầu từ state 0, ghé qua đủ 250 node ít nhất một lần.
```

Vì chỉ cần counter khác 0, mỗi state chỉ cần được ghé qua một lần là đủ. Cách đẹp nhất là tìm một **Hamiltonian path** gồm 250 node.

---

## 7. Extract graph từ binary

Mỗi state block trong disassembly có pattern gần giống nhau:

```asm
inc BYTE PTR [rsp+offset]
movzx edx,BYTE PTR [rdi+rcx*1]
cmp rdx, imm
ja finish
inc rcx
lea rsi,[rip+table]
movsxd rdx,DWORD PTR [rsi+rdx*4]
add rdx,rsi
jmp rdx
```

Cách extract:

1. Tìm tất cả instruction dạng:

```asm
inc BYTE PTR [rsp+...]
```

2. Mỗi instruction này đại diện cho một state.
3. Offset trong `[rsp+...]` chính là id counter, tương ứng state id.
4. Lấy `cmp rdx, imm` để biết input byte tối đa cho state đó.
5. Lấy địa chỉ jump table trong `.rodata`.
6. Mỗi entry trong jump table là một offset 32-bit signed.
7. Tính target:

```python
target_addr = table_base + signed_offset
```

8. Map `target_addr` về state tương ứng.

Lỗi gặp ban đầu: parser đọc hơi quá phạm vi của một state, nên lẫn table của state kế tiếp. Sau đó sửa bằng cách dừng parser tại block state tiếp theo.

Sau khi extract đúng, thu được:

```text
250 reachable states
khoảng 100 outgoing transitions mỗi state
```

Đồ thị khá dày, nên việc tìm đường đi qua đủ state khả thi.

---

## 8. Tìm đường đi Hamiltonian

Ta cần tìm danh sách label:

```text
label[0], label[1], ..., label[248]
```

Sao cho:

```text
state_0 --label[0]--> state_1
state_1 --label[1]--> state_2
...
state_248 --label[248]--> state_249
```

Và 250 state này không bị trùng, tức là đi qua đủ toàn bộ state.

Vì graph có nhiều cạnh, dùng DFS/backtracking là đủ tốt. Heuristic dùng trong solver:

- Ưu tiên đi sang state chưa thăm.
- Ưu tiên state có ít lựa chọn tiếp theo hơn trước.
- Nếu cụt đường thì backtrack.

Sau khi có 249 transition hợp lệ, append thêm `127` làm input cuối.

Payload cuối có 250 số:

```text
249 số đầu: transition hợp lệ để đi qua đủ 250 state
số cuối: 127 để ép invalid transition và gọi check_instance()
```

---

## 9. Solver

Solver cuối cùng dùng list label đã tìm được:

```python
#!/usr/bin/env python3
import socket
import ssl
import subprocess
import sys

LABELS = [
    39, 11, 35, 62, 68, 27, 23, 69, 10, 24,
    86, 70, 19, 16, 50, 38, 42, 55, 88, 70,
    57, 44, 18, 36, 38, 76, 63, 69, 6, 37,
    8, 3, 48, 58, 83, 11, 84, 74, 88, 5,
    11, 63, 51, 88, 11, 59, 28, 8, 47, 6,
    3, 41, 26, 17, 72, 34, 64, 3, 45, 67,
    80, 55, 16, 52, 29, 88, 70, 89, 6, 84,
    68, 8, 19, 86, 29, 23, 74, 71, 56, 99,
    55, 53, 78, 19, 10, 88, 67, 97, 69, 64,
    40, 55, 56, 77, 25, 46, 80, 38, 73, 71,
    92, 38, 61, 16, 29, 74, 11, 84, 44, 100,
    62, 22, 2, 62, 29, 14, 18, 84, 47, 24,
    104, 14, 89, 60, 41, 82, 63, 2, 77, 44,
    61, 56, 78, 43, 48, 92, 70, 82, 32, 11,
    66, 104, 83, 14, 13, 44, 5, 52, 74, 26,
    18, 16, 66, 100, 29, 21, 66, 34, 49, 104,
    9, 4, 36, 81, 99, 89, 6, 67, 7, 74,
    100, 37, 3, 39, 101, 11, 0, 83, 102, 53,
    90, 91, 1, 93, 29, 62, 51, 96, 38, 75,
    48, 26, 107, 33, 72, 5, 59, 22, 73, 83,
    5, 77, 55, 77, 40, 94, 24, 39, 48, 33,
    38, 58, 12, 45, 18, 22, 26, 56, 52, 21,
    43, 22, 68, 35, 75, 101, 87, 68, 71, 73,
    61, 5, 94, 24, 100, 6, 31, 45, 64, 36,
    1, 59, 38, 31, 69, 72, 30, 31, 27,
    127
]


def payload() -> bytes:
    assert len(LABELS) == 250
    return (";".join(map(str, LABELS)) + ";\n").encode()


def local(binary: str) -> int:
    p = subprocess.run(
        [binary],
        input=payload(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    sys.stdout.buffer.write(p.stdout)
    sys.stderr.buffer.write(p.stderr)
    return p.returncode


def remote(host: str, port: int) -> int:
    ctx = ssl.create_default_context()
    raw = socket.create_connection((host, port), timeout=15)
    s = ctx.wrap_socket(raw, server_hostname=host)
    s.settimeout(8)
    s.sendall(payload())

    out = bytearray()
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
    except socket.timeout:
        pass
    finally:
        s.close()

    sys.stdout.buffer.write(out)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "payload":
        sys.stdout.buffer.write(payload())
    elif sys.argv[1] == "local":
        raise SystemExit(local(sys.argv[2]))
    elif sys.argv[1] == "remote":
        raise SystemExit(remote(sys.argv[2], int(sys.argv[3])))
```

Payload sinh ra có dạng:

```bash
python3 solve.py payload > payload.txt
```

Sau đó có thể gửi bằng `ncat`:

```bash
python3 solve.py payload | ncat --ssl pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de 443
```

Hoặc dùng mode remote trong solver:

```bash
python3 solve.py remote pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de 443
```

---

## 10. Test local

Để chứng minh solver đúng ở local, tạo flag giả:

```bash
echo 'LOCAL_FLAG_KOENIGSBERG_OK' > /flag
```

Chạy solver local:

```bash
python3 solve.py local ./koenigsberg-delivery-problem/cartographer
```

Output:

```text
Congratulations! Here is your flag: LOCAL_FLAG_KOENIGSBERG_OK
```

Đây là bằng chứng local pass thật, vì binary chỉ in dòng `Congratulations` sau khi `check_instance()` xác nhận đủ 250 counter khác 0.

---

## 11. Remote

Lệnh remote cần chạy:

```bash
python3 solve.py remote pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de 443
```

Hoặc:

```bash
python3 solve.py payload | ncat --ssl pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de 443
```

Trong sandbox hiện tại, remote chưa lấy được flag vì lỗi DNS/network:

```text
socket.gaierror: [Errno -3] Temporary failure in name resolution
```

Kiểm tra thêm với domain khác như `google.com` và `kitctf.de` cũng không resolve được, nên lỗi nằm ở môi trường sandbox, không phải ở payload.

Khi chạy trên máy có Internet/DNS bình thường, payload này sẽ được gửi lên server và server sẽ in flag thật theo format của challenge.

---

## 12. Tóm tắt lời giải

1. Binary đọc 250 số dạng `%hhd;`.
2. Hàm `cfg()` coi mỗi số là một cạnh trong đồ thị 250 state.
3. Mỗi lần đi vào state `i`, counter `cnt[i]` tăng lên.
4. `check_instance()` chỉ in flag nếu tất cả 250 counter đều khác 0.
5. Vì invalid transition gọi `check_instance()`, ta cần:
   - đi qua đủ 250 state bằng 249 transition hợp lệ;
   - sau đó gửi một số invalid để trigger check.
6. Extract jump table từ `.rodata` để dựng graph.
7. Tìm Hamiltonian path từ state 0.
8. Append `127` làm transition invalid cuối.
9. Local pass và in flag giả thành công.
10. Remote payload sẵn sàng, nhưng sandbox không có DNS nên chưa lấy được flag thật trong runtime này.

---

## 13. Log thao tác

```text
[1] Extracted koenigsberg-delivery-problem.tar(1).gz.
[2] Identified ELF64 PIE binary: cartographer, not stripped.
[3] Reversed symbols: main(), cfg(), check_instance(). main() reads 250 signed-byte decimal values using scanf("%hhd;").
[4] check_instance(ptr, 0xfa) prints flag only when all 250 byte counters are non-zero.
[5] cfg() initializes 250 byte counters on stack, starts at state 0, increments current state's counter, reads a byte, dispatches via per-state jump tables, and calls check_instance() on invalid transition.
[6] Extracted all 250 state blocks and jump tables from .rodata. Initial extraction bug: parsing too many lines per state captured the next state's table; fixed by stopping at the next state block.
[7] Built directed graph: 250 reachable states, about 100 outgoing transitions per state.
[8] Found a Hamiltonian path from state 0 covering all 250 states, then appended invalid label 127 to force check_instance().
[9] Local proof: with /flag = LOCAL_FLAG_KOENIGSBERG_OK, running cartographer with payload prints: Congratulations! Here is your flag: LOCAL_FLAG_KOENIGSBERG_OK
[10] Remote attempt: python3 solve.py tried to connect to pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de:443 over SSL but sandbox DNS failed: socket.gaierror [Errno -3] Temporary failure in name resolution.
```
