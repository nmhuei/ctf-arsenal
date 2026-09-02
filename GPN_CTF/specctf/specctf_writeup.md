# Writeup — specCTF

## Thông tin challenge

- **Category:** Reverse Engineering / Speculative Execution
- **File:** `specctf.tar.gz`
- **Binary:** `specCTF`
- **Kết quả:** lấy được flag local

```text
GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}
```

---

## 1. Khảo sát ban đầu

Sau khi giải nén challenge:

```bash
mkdir -p specctf_work
cd specctf_work
tar -xzf ../specctf.tar.gz
file specctf/specCTF
```

Kết quả:

```text
specCTF: ELF 64-bit LSB pie executable, x86-64, dynamically linked, not stripped
```

Binary **không bị strip**, nên còn khá nhiều symbol hữu ích:

```bash
nm -C specctf/specCTF
```

Các symbol đáng chú ý:

```text
00000000000070c0 D ENC
0000000000001239 t hashy(unsigned long)
0000000000001363 T specEnvTime(unsigned long, int)
0000000000001c07 T specte_byte(unsigned long, int)
0000000000001d3a T main
```

Tên challenge là `specCTF`, trong binary cũng có nhiều hàm liên quan đến cache/timing/speculative execution như `train`, `readMemoryByte`, `specEnvTime`, `specte_byte`. Tuy nhiên phần quan trọng nhất vẫn là logic check flag trong `main` và hàm `hashy`.

---

## 2. Phân tích `main`

Disassemble `main`:

```bash
objdump -d -M intel --no-show-raw-insn specctf/specCTF
```

Đoạn chính trong `main`:

```asm
mov    rax,QWORD PTR [rbp-0x18]
mov    rdi,rax
call   strlen@plt

mov    rax,QWORD PTR [rbp-0x20]
and    eax,0x7
test   rax,rax
je     valid_length
```

Binary yêu cầu độ dài input chia hết cho 8.

Sau đó chương trình lặp theo từng block 8 byte:

```asm
lea    rax,[rip+0x52e8]        # ENC
mov    rax,QWORD PTR [rdx+rax]
mov    r15,rax                 # ENC[i]

mov    rax,QWORD PTR [input + i*8]
mov    r14,rax                 # input block 8 byte

call   specte_byte
```

Ý nghĩa logic:

```c
for (int i = 0; i < strlen(argv[1]) / 8; i++) {
    uint64_t expected = ENC[i];
    uint64_t block = *(uint64_t *)(argv[1] + i * 8);
    ok += specte_byte(...);
}
```

Sau khi check nhiều vòng, nếu đủ số block đúng thì in:

```text
CORRECT
```

Ngược lại in:

```text
NOPE
```

---

## 3. Dump mảng `ENC`

Dùng `readelf` để xác định vị trí và kích thước:

```bash
readelf -sW specctf/specCTF | grep ENC
```

`ENC` nằm ở `.data`, địa chỉ `0x70c0`.

Dump `.data`:

```bash
objdump -s -j .data specctf/specCTF
```

Các QWORD little-endian của `ENC`:

```python
ENC = [
    0xd4274db9b97175e5,
    0x7c56450361466e9a,
    0xd3a0f1efa162aeed,
    0x44cde0d9c2d3a245,
    0x80ed0ad29bd8aa41,
    0x991653a7bfbbe2ff,
]
```

Có 6 block, mỗi block 8 byte, vậy flag dài 48 byte.

---

## 4. Phân tích hàm `hashy`

Disassemble `hashy`:

```asm
hashy:
    mov    rax, input
    shr    rax, 0x21
    xor    input, rax

    movabs rdx, 0xf451af975d152cad
    imul   rax, rdx

    shr    rax, 0x21
    xor    input, rax

    movabs rax, 0xc2ceaade1a351c23
    xor    input, rax

    shr    rax, 0x21
    xor    input, rax
```

Viết lại dạng C:

```c
uint64_t hashy(uint64_t x) {
    x ^= x >> 33;
    x *= 0xf451af975d152cad;
    x ^= x >> 33;
    x ^= 0xc2ceaade1a351c23;
    x ^= x >> 33;
    return x;
}
```

Trong `specEnvTime`, chương trình so sánh:

```asm
call   hashy
cmp    rax, r15
sete   al
```

Tức là điều kiện đúng thực sự là:

```c
hashy(input_block) == ENC[i]
```

Phần speculative/timing chỉ dùng để làm rối và làm chương trình chạy chậm/khó đoán. Không cần khai thác side-channel nếu ta đảo ngược được `hashy`.

---

## 5. Đảo ngược hash

Hàm `hashy` gồm toàn các phép toán đảo được trên 64-bit:

1. `x ^= x >> 33`
2. `x *= constant` với constant lẻ nên có modular inverse modulo `2^64`
3. `x ^= constant`

### 5.1. Đảo `x ^= x >> 33`

Vì đây là xor với right shift, ta khôi phục bit từ bit cao xuống bit thấp.

```python
def unxorshr(y: int, shift: int = 33) -> int:
    x = 0
    for i in range(63, -1, -1):
        bit = (y >> i) & 1
        if i + shift < 64:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x & MASK
```

### 5.2. Đảo phép nhân modulo `2^64`

Do multiplier là số lẻ:

```python
MUL = 0xf451af975d152cad
inv_mul = pow(MUL, -1, 1 << 64)
```

### 5.3. Hàm inverse đầy đủ

Ta đảo các bước theo thứ tự ngược lại:

```python
def inv_hash(y: int) -> int:
    inv_mul = pow(MUL, -1, 1 << 64)
    x = unxorshr(y, 33)
    x ^= XOR
    x = unxorshr(x, 33)
    x = (x * inv_mul) & MASK
    x = unxorshr(x, 33)
    return x
```

---

## 6. Solver

```python
#!/usr/bin/env python3
from struct import pack

MASK = (1 << 64) - 1
MUL = 0xf451af975d152cad
XOR = 0xc2ceaade1a351c23
ENC = [
    0xd4274db9b97175e5,
    0x7c56450361466e9a,
    0xd3a0f1efa162aeed,
    0x44cde0d9c2d3a245,
    0x80ed0ad29bd8aa41,
    0x991653a7bfbbe2ff,
]


def unxorshr(y: int, shift: int = 33) -> int:
    x = 0
    for i in range(63, -1, -1):
        bit = (y >> i) & 1
        if i + shift < 64:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x & MASK


def hashy(x: int) -> int:
    x &= MASK
    x ^= x >> 33
    x = (x * MUL) & MASK
    x ^= x >> 33
    x ^= XOR
    x ^= x >> 33
    return x & MASK


def inv_hash(y: int) -> int:
    inv_mul = pow(MUL, -1, 1 << 64)
    x = unxorshr(y, 33)
    x ^= XOR
    x = unxorshr(x, 33)
    x = (x * inv_mul) & MASK
    x = unxorshr(x, 33)
    return x


blocks = [inv_hash(v) for v in ENC]
flag = b''.join(pack('<Q', b) for b in blocks)
print(flag.decode())

# Proof: re-hash each recovered block and compare against ENC.
assert all(hashy(b) == e for b, e in zip(blocks, ENC))
print('[ok] every recovered 8-byte block hashes back to ENC')
```

Chạy solver:

```bash
python3 solve_specctf.py
```

Output:

```text
GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}
[ok] every recovered 8-byte block hashes back to ENC
```

---

## 7. Bằng chứng flag đúng

Các block sau khi inverse:

```text
GPNCTF{
THIs_MeA1
_Is_5peC
Ul4t1V3L
y_de1ICI
Ou5!!!!}
```

Ghép little-endian theo từng block 8 byte thu được:

```text
GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}
```

Solver đã hash ngược lại từng block và assert:

```python
assert all(hashy(b) == e for b, e in zip(blocks, ENC))
```

Điều này chứng minh flag không chỉ là chuỗi nhìn giống flag, mà đúng với toàn bộ giá trị `ENC` trong binary.

Ngoài ra có thể patch local binary để bỏ phần timing/speculative-execution chậm và kiểm tra trực tiếp điều kiện `hashy(block) == ENC[i]`.

Kết quả test local:

```bash
./specCTF.fastcheck 'GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}'
# CORRECT

./specCTF.fastcheck 'GPNCTF{wrongwrongwrongwrongwrongwrongwrongwrongwrong}'
# NOPE
```

---

## 8. Flag

```text
GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}
```

---

## 9. Log thao tác

```bash
# Giải nén
mkdir -p /mnt/data/specctf_work
cd /mnt/data/specctf_work
tar -xzf /mnt/data/specctf.tar.gz

# Xem loại file
file specctf/specCTF

# Xem symbol vì binary chưa strip
nm -C specctf/specCTF

# Xem vị trí ENC
readelf -sW specctf/specCTF | grep ENC

# Dump data để lấy ENC
objdump -s -j .data specctf/specCTF

# Disassemble main và hashy
objdump -d -M intel --no-show-raw-insn specctf/specCTF

# Viết solver đảo hash
python3 solve_specctf.py

# Output
# GPNCTF{THIs_MeA1_Is_5peCUl4t1V3Ly_de1ICIOu5!!!!}
# [ok] every recovered 8-byte block hashes back to ENC
```

---

## Ghi chú về server

Trong file challenge và nội dung yêu cầu hiện tại không có host/port remote. Vì vậy bài này được xác minh local bằng binary và bằng điều kiện hash thật trong chương trình. Nếu có server remote, chỉ cần gửi chính flag trên làm argument/input theo format server yêu cầu.
