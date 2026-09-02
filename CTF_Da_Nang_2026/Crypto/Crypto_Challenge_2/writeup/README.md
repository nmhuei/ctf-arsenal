# Crypto Challenge 2 — Lattice in the Machine

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `297` |
| **Solves** | 3 |

## 📝 Description

Lattice in the Machine - quantum-safe AI communication console


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `server.py` | `platform_attachment` | ✅ Downloaded | [server.py](server.py) |
| `Dockerfile` | `platform_attachment` | ✅ Downloaded | [Dockerfile](Dockerfile) |
| `wrapper.sh` | `platform_attachment` | ✅ Downloaded | [wrapper.sh](wrapper.sh) |
| `docker-entrypoint.sh` | `platform_attachment` | ✅ Downloaded | [docker-entrypoint.sh](docker-entrypoint.sh) |

## 🚩 Flag & Solution

- [x] Solved

```
flag{eaf9371a-c77c-42fd-a2d8-5354659e954c}
```

### Writeup / Notes

1. **Phân tích thuật toán mã hóa (LWE - Learning With Errors)**:
   - Các tham số: $n = 50$, $q = 10007$, secret vector $s \in [-3, 3]^{50}$, noise $e \in \{-1, 0, 1\}$.
   - Mỗi mẫu thử `sample` trả về cặp $(a, b)$ thỏa mãn:
     $$b \equiv a \cdot s + e \pmod q$$
   - Khi mã hóa từng bit cờ (`encrypt`):
     - Bit $0$: $b \equiv a \cdot s + e \pmod q$
     - Bit $1$: $b \equiv a \cdot s + e + \lfloor q / 2 \rfloor \pmod q$

2. **Khai thác qua Kỹ thuật Nhúng Lattice Kannan (Kannan's Embedding Technique)**:
   - Thu thập $M = 90$ mẫu $(A, b)$.
   - Xây dựng ma trận cơ sở mạng $(M + n + 1) \times (M + n + 1)$:
     $$B = \begin{pmatrix} q \cdot I_M & 0 & 0 \\ A^T & I_n & 0 \\ b^T & 0 & 1 \end{pmatrix}$$
   - Vector mục tiêu trong mạng có dạng $v = (-e, s, -1)$. Do $\|v\| \approx 16 \ll q^{M/(M+n+1)} \approx 206$, vector này là vector ngắn nhất độc nhất (unique shortest vector).

3. **Chạy LLL Reduction & Giải mã**:
   - Sử dụng thư viện `fpylll` chạy thuật toán `LLL.reduction(mat)` trong chưa đầy 0.1 giây.
   - Thu hồi chính xác vector bí mật $s$.
   - Tính $centered(b - a \cdot s) \pmod q$: nếu $|val| < q/4 \approx 2500$ thì bit là $0$, ngược lại bit là $1$.
   - Giải mã bitstream thu được cờ hoàn chỉnh: **`flag{eaf9371a-c77c-42fd-a2d8-5354659e954c}`**.
