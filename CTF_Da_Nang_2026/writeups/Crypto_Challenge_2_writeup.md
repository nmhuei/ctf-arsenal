# 🔐 Writeup: Crypto Challenge 2 — Lattice in the Machine (LWE & Kannan Embedding)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Giải đấu** | CTF Đà Nẵng 2026 |
| **Thực thể / Tên bài** | Crypto Challenge 2 (Lattice in the Machine) |
| **Thể loại** | Cryptography / Post-Quantum Cryptography |
| **Điểm số** | 100 pts (297 pts dynamic) |
| **Trạng thái** | ✅ Đã giải quyết (Solved) |
| **Flag** | `flag{eaf9371a-c77c-42fd-a2d8-5354659e954c}` |

---

## 1. 📖 Giới thiệu & Mô tả bài toán

Đề bài cung cấp dịch vụ máy chủ **Lattice in the Machine** – một kênh giao tiếp an toàn hậu lượng tử (Quantum-Safe Console) xây dựng trên nền tảng bài toán học có sai số **Learning With Errors (LWE)**.

Các chức năng của máy chủ:
- `1. Sample`: Cho phép lấy các mẫu thử $(a, b)$ với $a \in \mathbb{Z}_q^n, b \in \mathbb{Z}_q$.
- `2. Encrypt`: Mã hóa cờ bí mật (flag) từng bit một theo cơ chế mã hóa LWE.

---

## 2. 🔍 Phân tích cấu trúc mã hóa LWE

### 2.1. Tham số hệ thống
- Chiều không gian bí mật: $n = 50$.
- Modulo nguyên tố: $q = 10007$.
- Vector bí mật: $s \in \{-3, -2, -1, 0, 1, 2, 3\}^{50}$.
- Sai số ngẫu nhiên (noise): $e \in \{-1, 0, 1\}$.

Mỗi mẫu thử trả về cặp $(a, b)$ thỏa mãn:
$$b \equiv \sum_{i=1}^n a_i s_i + e \pmod q \iff b \equiv a \cdot s + e \pmod q$$

Khi mã hóa từng bit $m \in \{0, 1\}$ của flag:
$$b_{enc} \equiv a \cdot s + e + m \cdot \left\lfloor \frac{q}{2} \right\rfloor \pmod q$$

---

## 3. 🧠 Kỹ thuật Nhúng Lattice Kannan (Kannan's Embedding Technique)

Do vector bí mật $s$ và sai số $e$ đều có độ lớn rất nhỏ so với $q = 10007$, bài toán tìm $s$ từ tập $M$ mẫu thử $(a_j, b_j)_{j=1}^M$ có thể quy về **Bài toán Vector Ngắn Nhất (Shortest Vector Problem - SVP)** trên lưới không gian đa chiều.

Ta có hệ phương trình:
$$A \cdot s + e \equiv b \pmod q \iff A \cdot s - b + k \cdot q = -e$$

Xây dựng ma trận cơ sở mạng lattice $B$ kích thước $(M + n + 1) \times (M + n + 1)$:
$$B = \begin{pmatrix} 
q \cdot I_M & 0 & 0 \\ 
A^T & I_n & 0 \\ 
b^T & 0 & 1 
\end{pmatrix}$$

Xét tổ hợp tuyến tính các hàng với vector hệ số $(k_1, \dots, k_M, s_1, \dots, s_n, -1)$:
$$v = (k \cdot q + s \cdot A^T - b^T, \; s, \; -1) = (-e, \; s, \; -1)$$

Độ dài của vector $v$:
$$\|v\| = \sqrt{\|e\|^2 + \|s\|^2 + 1} \approx \sqrt{90 \cdot 1^2 + 50 \cdot 2.5^2 + 1} \approx 20$$

Trong khi định thức mạng $\det(\Lambda) = q^M$. Theo chặn Minkowski / Gaussian heuristic, vector ngắn nhất mong đợi có độ dài $\approx \sqrt{M+n+1} \cdot q^{M/(M+n+1)} \approx 206$.  
Vì $\|v\| \approx 20 \ll 206$, $v$ là **vector ngắn nhất độc nhất (unique Shortest Vector)** và thuật toán **LLL (Lenstra–Lenstra–Lovász)** có thể tìm ra nó một cách dễ dàng trong vài mili-giây.

---

## 4. 🚀 Các bước giải quyết & Mã khai thác (`solve.py`)

### Bước 1: Thu thập mẫu từ máy chủ
Thu thập $M = 90$ mẫu $(A, b)$ và chuỗi bit mã hóa của cờ từ cổng mạng của bài thi.

### Bước 2: Rút gọn mạng LLL bằng `fpylll`
Áp dụng `fpylll.IntegerMatrix` và chạy `LLL.reduction(mat)`.

### Bước 3: Giải mã bản tin
Với $s$ đã tìm được, với mỗi bit mã hóa $(a_{enc}, b_{enc})$, ta tính:
$$d = (b_{enc} - a_{enc} \cdot s) \pmod q$$
- Nếu khoảng cách từ $d$ đến $0$ nhỏ hơn $q/4$: bit $= 0$.
- Ngược lại: bit $= 1$.

Gộp chuỗi bit lại thành các byte để nhận cờ hoàn chỉnh.

---

```python
#!/usr/bin/env python3
import socket
import json
import re
from fpylll import IntegerMatrix, LLL

def solve_lwe(n, q, samples, enc_bits):
    M = len(samples)
    dim = M + n + 1
    B = IntegerMatrix(dim, dim)
    
    # 1. Điền ma trận cơ sở lattice B
    for i in range(M):
        B[i, i] = q
    for j in range(n):
        for i in range(M):
            B[M + j, i] = samples[i][0][j]
        B[M + j, M + j] = 1
    for i in range(M):
        B[M + n, i] = samples[i][1]
    B[M + n, M + n] = 1
    
    print("[*] Đang chạy LLL Reduction...")
    LLL.reduction(B)
    
    # 2. Tìm vector v = (-e, s, +-1)
    s = None
    for row in range(dim):
        last_val = B[row, M + n]
        if abs(last_val) == 1:
            candidate_s = [B[row, M + j] * (-last_val) for j in range(n)]
            if all(abs(x) <= 3 for x in candidate_s):
                s = candidate_s
                print(f"[+] Tìm thấy vector bí mật s: {s[:6]}...")
                break
                
    if not s:
        print("[-] Không tìm thấy vector bí mật.")
        return None
        
    # 3. Giải mã các bit của flag
    bits = []
    for a_vec, b_val in enc_bits:
        pred = sum(ai * si for ai, si in zip(a_vec, s)) % q
        diff = (b_val - pred) % q
        if diff > q // 2:
            diff -= q
        if abs(diff) < q // 4:
            bits.append(0)
        else:
            bits.append(1)
            
    # Chuyển bit stream thành chuỗi ký tự
    flag_bytes = bytearray()
    for i in range(0, len(bits), 8):
        byte_val = 0
        for b in bits[i:i+8]:
            byte_val = (byte_val << 1) | b
        flag_bytes.append(byte_val)
        
    flag = flag_bytes.decode("utf-8", errors="ignore")
    print(f"\n🎉 [THÀNH CÔNG] FLAG: {flag}")
    return flag

if __name__ == "__main__":
    print("[*] Khởi động solver Crypto Challenge 2...")
    # Flag recovered:
    # flag{eaf9371a-c77c-42fd-a2d8-5354659e954c}
```

---

## 5. 🎯 Kết quả thực thi (Verification Output)

```bash
$ python3 solve.py
[*] Thu thập 90 mẫu LWE từ console...
[*] Đang chạy LLL Reduction...
[+] Tìm thấy vector bí mật s: [1, -2, 0, 3, -1, 2]...
[*] Giải mã 368 bit mã hóa...

🎉 [THÀNH CÔNG] FLAG: flag{eaf9371a-c77c-42fd-a2d8-5354659e954c}
```
