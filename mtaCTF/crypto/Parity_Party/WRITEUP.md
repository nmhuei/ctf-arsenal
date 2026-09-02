# Writeup CTF: Parity_Party

- **Category:** Crypto
- **Target:** `mta-ctf-60.id.vn:6002`
- **Flag:** `MTA60{par1ty_p4rty_1s_n0t_s0_easy}`

---

## 1. Phân tích bài toán

File mã nguồn [`chall.py`](chall.py) thực hiện mã hóa RSA chuẩn:
- Cặp khóa RSA 1024-bit: $N = p \cdot q$ với $p, q \approx 512$ bit, $e = 65537$.
- Flag $m$ được mã hóa thành bản mã: $c = m^e \pmod N$.
- Server cung cấp cho người chơi các tham số công khai: $N, e, c$.
- Cho phép người chơi gửi tối đa 1024 bản mã $ct$ bất kỳ và trả về bit chẵn lẻ của bản rõ sau giải mã:
  $$\text{Parity} = (ct^d \pmod N) \pmod 2$$

Đây là dạng bài toán mật mã kinh điển: **RSA Parity Oracle (LSB Oracle Attack)**.

---

## 2. Cơ sở lý thuyết (RSA Parity Oracle Attack)

Do tính chất đồng cấu nhân của hệ mật mã RSA:
$$(c \cdot 2^e)^d \equiv c^d \cdot (2^e)^d \equiv m \cdot 2 \pmod N$$

### Phân tích bước 1:
Xét giá trị $2m \pmod N$:
1. Nếu $2m < N$:
   - $2m \pmod N = 2m$ là số **chẵn** $\implies \text{Parity} = 0$.
   - Suy ra: $m \in [0, \frac{N}{2})$.
2. Nếu $2m \ge N$:
   - $2m \pmod N = 2m - N$.
   - Do $N$ là tích 2 số nguyên tố lẻ nên $N$ là số lẻ $\implies 2m - N$ là số **lẻ** $\implies \text{Parity} = 1$.
   - Suy ra: $m \in [\frac{N}{2}, N)$.

### Tổng quát hóa các bước tiếp theo (Binary Search):
Tại bước $k$ ($1 \le k \le 1024$), ta truy vấn bản mã:
$$c_k = c \cdot (2^k)^e \pmod N$$
Bản rõ tương ứng được giải mã là:
$$pt_k = (2^k \cdot m) \pmod N$$

Ta duy trì khoảng giá trị khả dĩ $[L, R]$ của $m$ (ban đầu $[L, R] = [0, N]$):
- $mid = \frac{L + R}{2}$
- Nếu $\text{Parity} == 1 \implies L = mid$
- Nếu $\text{Parity} == 0 \implies R = mid$

Vì $N \approx 2^{1024}$, sau đúng 1024 lần chia đôi không gian tìm kiếm, khoảng $[L, R]$ sẽ thu hẹp về một số nguyên duy nhất chính là $m$.

---

## 3. Kỹ thuật tối ưu hóa tốc độ (TCP Pipelining)

### Vấn đề:
Nếu gửi tuần tự từng truy vấn (gửi 1 bản mã $\rightarrow$ đợi nhận 1 kết quả $\rightarrow$ gửi tiếp), ta sẽ mất $1024 \times \text{RTT}$ (Round Trip Time). Nếu độ trễ mạng là 20-30ms, tổng thời gian giải mã có thể mất hơn 20–30 giây.

### Tối ưu hóa:
Quan sát công thức bản mã truy vấn:
$$c_k = c \cdot 2^{k \cdot e} \pmod N$$
Giá trị $c_k$ **hoàn toàn độc lập** với phản hồi của các truy vấn trước đó.

Do đó:
1. **Precomputation:** Tính trước toàn bộ 1024 bản mã $c_1, c_2, \dots, c_{1024}$.
2. **Pipelining / Bulk Sending:** Ghép nối và gửi toàn bộ 1024 bản mã qua socket trong **1 lần gửi duy nhất**.
3. **TCP_NODELAY:** Tắt thuật toán Nagle để gửi gói tin ngay lập tức.
4. **Bulk Reading:** Đọc liên tục 1024 kết quả `Parity` trả về từ server và thực hiện thu hẹp khoảng $[L, R]$ cục bộ trên CPU.

Thời gian chạy thực tế giảm từ **~25 giây** xuống **chưa đến 1 giây**.

---

## 4. Mã nguồn giải mã ([solve.py](solve.py))

```python
#!/usr/bin/env python3
import sys
import os
import subprocess
import socket
from decimal import Decimal, getcontext
from Crypto.Util.number import long_to_bytes

# Đặt độ chính xác Decimal đủ lớn cho tìm kiếm nhị phân 1024-bit
getcontext().prec = 1000

class LocalInterface:
    def __init__(self, cmd):
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def readline(self):
        return self.proc.stdout.readline()

    def sendall_lines(self, lines):
        payload = "\n".join(lines) + "\n"
        self.proc.stdin.write(payload)
        self.proc.stdin.flush()

    def close(self):
        self.proc.kill()


class RemoteInterface:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((host, port))
        self.reader = self.sock.makefile('r', buffering=1)
        self.writer = self.sock.makefile('w', buffering=1)

    def readline(self):
        return self.reader.readline()

    def sendall_lines(self, lines):
        payload = "\n".join(lines) + "\n"
        self.writer.write(payload)
        self.writer.flush()

    def close(self):
        self.sock.close()


def solve_fast(io):
    # Đọc tham số RSA từ server
    n_line = io.readline().strip()
    e_line = io.readline().strip()
    c_line = io.readline().strip()

    n = int(n_line.split("=")[1].strip())
    e = int(e_line.split("=")[1].strip())
    c = int(c_line.split("=")[1].strip())

    print(f"[*] N = {n}")
    print(f"[*] e = {e}")
    print(f"[*] c = {c}")

    # Tính trước 1024 bản mã
    print("[*] Precomputing all 1024 ciphertexts...")
    mult = pow(2, e, n)
    ct_list = []
    current_c = c
    for _ in range(1024):
        current_c = (current_c * mult) % n
        ct_list.append(str(current_c))

    # Gửi toàn bộ 1024 bản mã qua socket
    print("[*] Sending all 1024 queries at once (pipelining)...")
    io.sendall_lines(ct_list)

    # Đọc 1024 phản hồi parity
    print("[*] Reading all parity responses...")
    parities = []
    for _ in range(1024):
        line = io.readline()
        while "Parity:" not in line:
            line = io.readline()
        parity = int(line.split(":")[-1].strip())
        parities.append(parity)

    # Nhị phân tìm m
    low = Decimal(0)
    high = Decimal(n)
    for parity in parities:
        mid = (low + high) / 2
        if parity == 1:
            low = mid
        else:
            high = mid

    for cand in [int(high), int(low), int(high) - 1, int(low) + 1]:
        recovered = long_to_bytes(cand)
        if b"{" in recovered and b"}" in recovered:
            print(f"[+] Flag found: {recovered.decode('latin1', errors='ignore')}")
            return recovered

    res = long_to_bytes(int(high))
    print(f"[+] Decrypted: {res}")
    return res


if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        print(f"[*] Connecting to {host}:{port}...")
        io = RemoteInterface(host, port)
    else:
        print("[*] Running locally with chall.py...")
        chall_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chall.py")
        io = LocalInterface([sys.executable, chall_path])

    try:
        solve_fast(io)
    finally:
        io.close()
```

---

## 5. Kết quả thực thi

```bash
$ python3 solve.py mta-ctf-60.id.vn 6002
[*] Connecting to mta-ctf-60.id.vn:6002...
[*] N = 136299094910470587211775313622165813143433690825525833537660932482998548895693106538453326681031647880560002587909855795934494020679603264367135868766308918467954175000269548710438537036802913745082268940089045277082495026750672906472149119386455248073623630640219712793202385720258871575907130837918019264137
[*] e = 65537
[*] c = 75383445918451940460800360265052650138441731889248887722162950164766081663271809896465515536539179565700262577141143051281737797038301549359073823636349301966398663187832902585431434062990310884507182798837638277705322927685857952415078275065179051769890487236651093259583365535707370797741048028827218280898
[*] Precomputing all 1024 ciphertexts...
[*] Sending all 1024 queries at once (pipelining)...
[*] Reading all parity responses...
[+] Flag found: MTA60{par1ty_p4rty_1s_n0t_s0_easy}
```
