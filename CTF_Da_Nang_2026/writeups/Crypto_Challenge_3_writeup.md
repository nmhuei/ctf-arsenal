# 🔐 Writeup: Crypto Challenge 3 — NovaSign (ECDSA Nonce Reuse)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Giải đấu** | CTF Đà Nẵng 2026 |
| **Thực thể / Tên bài** | Crypto Challenge 3 (NovaSign) |
| **Thể loại** | Cryptography (Mật mã học) |
| **Điểm số** | 150 pts (600 pts dynamic) |
| **Trạng thái** | ✅ Đã giải quyết (Solved) |
| **Flag** | `flag{ec0d141f-7b8b-4e1e-b4c7-ed4a154651c7}` |

---

## 1. 📖 Giới thiệu & Mô tả bài toán

> *"Some Things Are Only Safe Because They Were Never Supposed to Happen Twice"*  
> *(Có những điều chỉ an toàn vì chúng không bao giờ được phép lặp lại hai lần)*

Mục tiêu là dịch vụ **NovaSign** – một cổng ký điện tử cho các phản hồi mô hình AI sử dụng thuật toán chữ ký số ECDSA trên đường cong elliptic chuẩn **`secp256k1`** kết hợp hàm băm **SHA-256**.

Các API endpoint được cung cấp:
- `GET /api/pubkey`: Trả về Public Key / Verifying Key $(Q_x, Q_y)$ của hệ thống.
- `GET /api/sign`: Trả về một chuỗi JSON phản hồi kèm chữ ký số ECDSA hợp lệ $(r, s)$.
- `POST /api/redeem`: Nhận payload `{"message": "give_flag", "r": "0x...", "s": "0x..."}`. Nếu chữ ký hợp lệ ứng với public key của server, hệ thống sẽ trả về cờ (flag).

---

## 2. 🔍 Phân tích mã nguồn & Cơ sở lý thuyết

### 2.1. Cơ chế ký ECDSA trên đường cong Elliptic
Theo chuẩn ECDSA trên đường cong `secp256k1`:
- Đường cong có bậc modulo nguyên tố $n$:
  $$n = \text{0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141}$$
- Private Key $d \in [1, n-1]$.
- Public Key $Q = d \cdot G$ (với $G$ là điểm sinh - Base Point).
- Với mỗi thông điệp $m$, máy chủ sinh một giá trị ngẫu nhiên tạm thời (ephemeral nonce) $k \in [1, n-1]$.
- Tọa độ điểm ký $R = k \cdot G = (x_R, y_R)$, suy ra:
  $$r = x_R \pmod n$$
- Giá trị chữ ký thứ hai $s$ được tính theo công thức:
  $$s \equiv k^{-1} (z + r \cdot d) \pmod n$$
  *(Trong đó $z = \text{int}(\text{SHA256}(m))$ là giá trị băm của thông điệp)*.

### 2.2. Lỗ hổng Tái sử dụng Nonce (ECDSA Nonce Reuse)
Lỗ hổng cốt lõi xuất hiện khi hàm sinh số ngẫu nhiên của máy chủ bị lỗi dẫn đến việc **tái sử dụng cùng một giá trị nonce $k$** cho hai thông điệp khác nhau $m_1 \neq m_2$.

Khi $k_1 = k_2 = k$, tọa độ $R_1 = R_2 \implies r_1 = r_2 = r$.

Ta có hệ phương trình:
$$\begin{cases} s_1 \equiv k^{-1} (z_1 + r \cdot d) \pmod n \\ s_2 \equiv k^{-1} (z_2 + r \cdot d) \pmod n \end{cases}$$

Lấy $(1) - (2)$:
$$s_1 - s_2 \equiv k^{-1} (z_1 - z_2) \pmod n$$

Từ đây, ta tính trực tiếp được nonce $k$:
$$k \equiv (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod n$$

Khi đã khôi phục được $k$, ta tính ngược lại **Private Key $d$**:
$$d \equiv r^{-1} (s_1 \cdot k - z_1) \pmod n$$

---

## 3. 🚀 Các bước khai thác chi tiết (Step-by-Step Exploitation)

### Bước 1: Thu thập mẫu chữ ký (Signature Harvesting)
Gửi liên tiếp các request `GET /api/sign` (khoảng 50–100 requests) và lưu trữ lại danh sách các cặp $(m, r, s)$. Khi phát hiện 2 bản tin có cùng giá trị $r$, ta dừng lại.

### Bước 2: Khôi phục Khóa bí mật (Private Key Recovery)
1. Tính băm $z_1 = \text{SHA256}(m_1)$ và $z_2 = \text{SHA256}(m_2)$.
2. Tính $k = (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod n$.
3. Tính $d = r^{-1} \cdot (s_1 \cdot k - z_1) \pmod n$.
4. Kiểm tra $d \cdot G$ so với Public Key $Q_x$ lấy từ `/api/pubkey` để xác nhận $d$ chính xác 100%.

### Bước 3: Giả mạo chữ ký & Nhận Flag (Signature Forgery)
1. Sử dụng Private Key $d$ đã khôi phục để ký thông điệp `"give_flag"`.
2. Gửi request `POST /api/redeem` kèm chữ ký giả mạo $(r_{forged}, s_{forged})$.
3. Server xác thực thành công và trả về flag.

---

## 4. 💻 Mã khai thác hoàn chỉnh (`solve.py`)

```python
#!/usr/bin/env python3
import requests
import urllib3
import hashlib
import json
from ecdsa import SECP256k1, SigningKey

urllib3.disable_warnings()

TARGET = "https://370a0c93-475f-4c09-91da-532043e9afb4.222.255.138.122.nip.io"
CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def solve():
    # 1. Lấy Public Key của máy chủ
    print("[*] Đang lấy Public Key từ server...")
    r_pub = requests.get(f"{TARGET}/api/pubkey", verify=False)
    pub_data = r_pub.json()
    qx_target = pub_data["Qx"]
    print(f"[+] Server Public Key Qx: {qx_target}")

    # 2. Thu thập chữ ký để tìm va chạm Nonce (r trùng nhau)
    print("[*] Đang thu thập chữ ký để tìm nonce reuse...")
    r_seen = {}
    m1, m2, r_val, s1, s2 = None, None, None, None, None

    for i in range(150):
        res = requests.get(f"{TARGET}/api/sign", verify=False).json()
        r_hex = res["r"]
        if r_hex in r_seen:
            sig1 = r_seen[r_hex]
            sig2 = res
            m1, m2 = sig1["message"], sig2["message"]
            r_val = int(r_hex, 16)
            s1 = int(sig1["s"], 16)
            s2 = int(sig2["s"], 16)
            print(f"[+] Tìm thấy cặp Nonce Reuse tại lần request thứ {i+1}!")
            break
        r_seen[r_hex] = res

    if not m1:
        print("[-] Chưa tìm thấy nonce trùng lặp trong số mẫu đã lấy.")
        return None

    # 3. Tính toán khôi phục Private Key d
    z1 = int.from_bytes(hashlib.sha256(m1.encode()).digest(), "big")
    z2 = int.from_bytes(hashlib.sha256(m2.encode()).digest(), "big")

    k = ((z1 - z2) * pow(s1 - s2, -1, CURVE_N)) % CURVE_N
    d = (pow(r_val, -1, CURVE_N) * (s1 * k - z1)) % CURVE_N

    sk = SigningKey.from_secret_exponent(d, curve=SECP256k1)
    vk = sk.get_verifying_key()
    qx_rec = hex(vk.pubkey.point.x())
    print(f"[+] Khôi phục thành công Private Key d: {hex(d)}")
    print(f"[*] Kiểm tra Public Key Qx tái tạo: {qx_rec} (Khớp: {qx_rec == qx_target})")

    # 4. Ký giả mạo thông điệp 'give_flag' và gửi đến /api/redeem
    msg = b"give_flag"
    sig = sk.sign_deterministic(msg, hashfunc=hashlib.sha256)
    r_forged = int.from_bytes(sig[:32], "big")
    s_forged = int.from_bytes(sig[32:], "big")

    payload = {
        "message": "give_flag",
        "r": hex(r_forged),
        "s": hex(s_forged)
    }

    print("[*] Đang gửi payload giả mạo đến /api/redeem...")
    r_redeem = requests.post(f"{TARGET}/api/redeem", json=payload, verify=False)
    redeem_data = r_redeem.json()
    flag = redeem_data.get("flag")
    print(f"\n🎉 [THÀNH CÔNG] FLAG: {flag}")
    return flag

if __name__ == "__main__":
    solve()
```

---

## 5. 🎯 Kết quả thực thi (Verification Output)

```bash
$ python3 solve.py
[*] Đang lấy Public Key từ server...
[+] Server Public Key Qx: 0x339340662663134abeea659793d53fabd8ad9fe56c5d206f98a81a2ff356f3c5
[*] Đang thu thập chữ ký để tìm nonce reuse...
[+] Tìm thấy cặp Nonce Reuse tại lần request thứ 42!
[+] Khôi phục thành công Private Key d: 0x9dd33bcd11bd9a64cb95712110337768f84583b4d7dfef72d5e1564de1c88340
[*] Kiểm tra Public Key Qx tái tạo: 0x339340662663134abeea659793d53fabd8ad9fe56c5d206f98a81a2ff356f3c5 (Khớp: True)
[*] Đang gửi payload giả mạo đến /api/redeem...

🎉 [THÀNH CÔNG] FLAG: flag{ec0d141f-7b8b-4e1e-b4c7-ed4a154651c7}
```
