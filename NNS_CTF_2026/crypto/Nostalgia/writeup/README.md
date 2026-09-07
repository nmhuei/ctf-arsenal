# Writeup: Nostalgia

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `363` |
| **Author** | `Zukane` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Bài toán khởi tạo seed bằng hàm thời gian `seed = time.time()` và bình luận trêu ngươi rằng độ chính xác nanosecond sẽ khiến việc dò seed bất khả thi. Sau đó, biến `seed` được cập nhật qua 1337 bước của bộ sinh số ngẫu nhiên tuyến tính LCG modulo $2^{32}$. Giá trị cuối cùng được hash bằng SHA-256 để tạo khóa AES-ECB mã hóa flag.

---

## 🔍 Vulnerability Analysis
1. **Lỗi ép kiểu làm mất độ chính xác nanosecond:**
   - Trong hàm LCG:
     $$\text{lcg}(s) = (16843009 \cdot \text{int}(s) + 826366247) \pmod{2^{32}}$$
   - Phép gọi `int(s)` ngay trong vòng lặp đầu tiên đã cắt cụt toàn bộ phần thập phân (microsecond / nanosecond), biến seed thực chất chỉ là một số nguyên giây Unix timestamp: $t = \lfloor \text{time.time()} \rfloor$.
2. **Thu gọn 1337 bước lặp affine:**
   - Một phép biến đổi affine $s \mapsto a \cdot s + b \pmod m$ lặp lại $k$ lần tương đương với một phép biến đổi affine duy nhất:
     $$s_k = (a^k \cdot s_0 + b \cdot \frac{a^k - 1}{a - 1}) \pmod m$$
   - Với $k = 1337, a = 16843009, b = 826366247, m = 2^{32}$, toàn bộ chuỗi lặp được rút gọn thành:
     $$s_{1337} = (586823937 \cdot t + 3067822255) \pmod{2^{32}}$$
3. **Không gian tìm kiếm timestamp cực nhỏ:**
   - Dựa vào mốc thời gian metadata của file thử thách khi được tạo hoặc upload lên giải, ta chỉ cần quét một khoảng vài ngày quanh mốc đó (khoảng $\pm 2 \times 10^5$ giây). Mỗi giây chỉ mất một phép nhân cộng số nguyên và một lần kiểm tra AES block đầu tiên.

---

## 🎯 Solution Flow (Không dùng code)
1. **Rút gọn toán học chuỗi lặp LCG:**
   - Tính trước hệ số tổng hợp $(A, B)$ biểu diễn bước chuyển đổi sau 1337 vòng modulo $2^{32}$.
2. **Xác định mốc thời gian gốc (Baseline Timestamp):**
   - Đọc thời gian sửa đổi (mtime) của file hoặc thời điểm bắt đầu giải đấu để làm tâm điểm tìm kiếm.
3. **Dò quét thời gian theo dạng bán kính (Radius Sweep):**
   - Với mỗi candidate timestamp nguyên $t$ từ tâm ra hai phía:
     - Tính trực tiếp $seed_{1337} = (A \cdot t + B) \pmod{2^{32}}$.
     - Tạo khóa AES bằng $\text{SHA-256}(\text{str}(seed_{1337}))$.
     - Thử giải mã 16 byte đầu của bản mã; nếu bắt đầu bằng `NNS{`, ta đã tìm ra đúng timestamp và dừng vòng lặp.
4. **Giải mã toàn bộ bản mã:**
   - Dùng khóa AES đã tìm thấy để giải mã toàn bộ khối và bóc tách padding PKCS#7 để thu được flag.

---

## 🚩 Flag
`NNS{th3_b3st_t1m3_t0_m4k3_m3m0r13s_15_n0w}`
