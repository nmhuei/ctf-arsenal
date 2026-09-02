# Pwn Challenge 1

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `83` |
| **Solves** | 6 |

## 📝 Description

The Machine That Remembers Too Much


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `punchcard` | `platform_attachment` | ✅ Downloaded | [punchcard](punchcard) |

## 🚩 Flag & Solution

- [x] Solved

```
flag{04d062eb-7d1c-40e6-96fa-859d777bacc9}
```

### Writeup / Notes

1. **Phân tích nhị phân (`punchcard`)**:
   - Kiến trúc: `ELF 32-bit LSB executable, Intel i386`.
   - Bảo mật:
     - RELRO: `Partial RELRO`
     - Stack Canary: `No canary found`
     - NX: `Disabled (Stack executable)`
     - PIE: `No PIE (0x8048000)`
   - Trong chương trình có hàm `win()` tại địa chỉ `0x080491d6`. Hàm này đọc biến môi trường `FLAG` và in ra kết quả.
   - Hàm `process_punchcard()` sử dụng hàm nguy hiểm `gets(&buf)` để đọc dữ liệu punch card từ người dùng:
     - Buffer nằm tại `ebp - 0x48` (72 bytes).
     - Saved EBP: 4 bytes.
     - Saved EIP: 4 bytes.
     - Tổng offset để ghi đè địa chỉ trả về (Return Address / EIP) là `72 + 4 = 76` bytes.

2. **Khai thác (Buffer Overflow / ret2win)**:
   - Payload: `'A' * 76 + p32(0x080491d6)`
   - Gửi payload sau khi gặp prompt `CARD> `.
   - Hàm `process_punchcard()` khi `ret` sẽ nhảy thẳng vào hàm `win()`.

3. **Chạy script**:
   - Local: `python3 solve.py`
   - Remote: `python3 solve.py REMOTE HOST=<IP/Domain> PORT=<PORT>`

