# Writeup: NRT

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Thorbeam` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Bài toán cài đặt một thuật toán sinh modulus RSA $N$ kích thước 4096-bit. Để tăng tốc sinh số, tác giả nhân liên tiếp các số nguyên tố nhỏ 24-bit cho đến khi tích vượt quá `SMALL_BITS = 256`, sau đó mới nhân tiếp các số nguyên tố lớn để đạt kích thước 4096 bit. Bản rõ flag được đảm bảo có độ dài nhỏ hơn 256-bit:
$$m = \text{bytes\_to\_long}(flag) < 2^{256}$$

---

## 🔍 Vulnerability Analysis
1. **Thừa số nguyên tố cực nhỏ:**
   - Các ước nguyên tố đầu tiên $p_1, p_2, \dots, p_k$ của $N$ chỉ có độ dài 24-bit ($p_i < 2^{24} \approx 1.6 \times 10^7$).
   - Các ước số này có thể dễ dàng tách ra bằng thuật toán chia thử (trial division) hoặc sàng nguyên tố trong chưa đầy 1 giây.
2. **Khai thác Định lý Thặng dư Trung Hoa (CRT):**
   - Tích của các ước nguyên tố nhỏ thỏa mãn: $M = \prod_{i=1}^k p_i > 2^{256}$.
   - Vì bản rõ $m < 2^{256} < M$, nên theo định lý CRT, việc biết toàn bộ thặng dư $m \pmod{p_i}$ với mọi $i \in \{1, \dots, k\}$ là đủ để khôi phục chính xác 100% giá trị $m$ trên tập số nguyên $\mathbb{Z}$ mà **hoàn toàn không cần phân tích các thừa số nguyên tố lớn còn lại của $N$**.

---

## 🎯 Solution Flow (Không dùng code)
1. **Phân tích thừa số nguyên tố nhỏ:**
   - Dùng thuật toán phân tích nhân tử với giới hạn cận trên $2^{24}$ để tách toàn bộ 11 thừa số nguyên tố 24-bit từ $N$.
2. **Giải mã cục bộ modulo từng số nguyên tố nhỏ:**
   - Với mỗi số nguyên tố $p_i$, tính số mũ giải mã cục bộ:
     $$d_i = e^{-1} \pmod{p_i - 1}$$
   - Tính thặng dư của bản rõ:
     $$m_i = ct^{d_i} \pmod{p_i}$$
3. **Tổng hợp nghiệm bằng Định lý Thặng dư Trung Hoa:**
   - Áp dụng CRT trên hệ thặng dư $\{m_i \pmod{p_i}\}_{i=1}^{11}$ để tìm $m \pmod{\prod p_i}$.
   - Do $m < \prod p_i$, nghiệm thu được chính là số nguyên $m$.
   - Chuyển đổi $m$ sang chuỗi byte ASCII để nhận flag.

---

## 🚩 Flag
`NNS{n0_n33d_f0r_4ll_pr1m35}`
