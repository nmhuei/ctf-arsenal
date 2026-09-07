# Writeup: Light-Weight Encryption

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Zukane` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Thử thách triển khai lược đồ mã hóa Compact-LWE (Learning With Errors dạng nén) với các tham số:
- Modulus $q = 2^{768}$.
- Ma trận công khai $A \in [0, 16)^{112 \times 16}$ gồm các số nguyên nhỏ.
- Khóa bí mật $s \in \mathbb{Z}_q^{16}$, vector lỗi $e \in [0, 2^{32})^{112}$, số nguyên tố $sk \approx 2^{128}$ và $p \approx 2^{520}$.
- Khóa công khai $B = A \cdot s + k \cdot e \pmod q$ với hệ số tỉ lệ $k \equiv p/sk \pmod q$.
- Bản mã gồm $c_1 = \sum_{i \in I} A_i$ và $c_2 = pt - \sum_{i \in I} B_i \pmod q$ với tập chỉ số ngẫu nhiên $|I| = 130$.

---

## 🔍 Vulnerability Analysis
Lược đồ này mắc phải lỗ hổng nghiêm trọng đã được công bố trong bài báo nghiên cứu *"A Polynomial-Time Attack on the Compact-LWE Scheme"* ([IACR ePrint 2017/742](https://eprint.iacr.org/2017/742.pdf)):
1. **Khử hoàn toàn thành phần khóa $s$ bằng nhân tử hạt nhân (Kernel Orthogonality):**
   - Do ma trận $A$ có kích thước $112 \times 16$, hạt nhân trái (left kernel) của $A$ trên $\mathbb{Z}$ có số chiều rất lớn: $112 - 16 = 96$.
   - Mọi vector hàng $u \in \ker_L(A)$ thỏa mãn $u \cdot A = 0$.
   - Khi nhân $u$ với khóa công khai $B$:
     $$u \cdot B \equiv u \cdot (A \cdot s + k \cdot e) \equiv k \cdot (u \cdot e) \pmod q$$
   - Nhân cả hai vế với $sk$ (sử dụng đẳng thức $sk \cdot k \equiv p \pmod q$):
     $$sk \cdot (u \cdot B) \equiv p \cdot (u \cdot e) \pmod q$$
2. **Khôi phục $sk$ và $p$ bằng Lưới Kannan CVP:**
   - Vì $|p \cdot (u \cdot e)| \approx 2^{520 + 40} = 2^{560} \ll q = 2^{768}$, giá trị sai số modulo $q$ không bị cuốn vòng (no wraparound).
   - Thiết lập một lưới ẩn (hidden linear form lattice) chiều nhỏ (ví dụ chiều 9) với trọng số chuẩn hóa $W = 2^{433}$ và rút gọn bằng `flatter`, vector ngắn nhất trực tiếp tiết lộ số nguyên tố bí mật $sk$ (128-bit).
   - Khi đã có $sk$, tính $\gcd$ của các sai số $sk \cdot (u_i \cdot B) \bmod^\pm q$ để cô lập chính xác số nguyên tố $p$ (520-bit).
3. **Giải mã triệt tiêu mà không cần tìm vector chỉ số $I$:**
   - Ma trận $A$ có các ước số bất biến trong dạng chuẩn tắc Smith (Smith Normal Form) đều bằng 1. Điều này chứng minh tồn tại một ma trận nghịch đảo trái nguyên $L \in \mathbb{Z}^{16 \times 112}$ thỏa mãn $L \cdot A = I_{16}$.
   - Quan hệ mã hóa cho thấy:
     $$sk \cdot (c_2 + c_1 \cdot s) \equiv sk \cdot pt - p \cdot (x \cdot e) \pmod q$$
   - Vì sai số nhân với $p$ hoàn toàn biến mất khi xét modulo $p$, và độ lớn tổng thể trên $\mathbb{Z}$ nhỏ hơn $q/2$, ta giải mã trực tiếp bản rõ mà không cần khôi phục vector ngẫu nhiên $x$:
     $$pt \equiv sk^{-1} \cdot ([sk \cdot c_2 + c_1 \cdot S'] \bmod^\pm q) \pmod p$$

---

## 🎯 Solution Flow (Không dùng code)
1. **Tính hạt nhân trái của ma trận $A$:**
   - Tìm không gian nghiệm trái $\ker_L(A)$ có số chiều 96 trên $\mathbb{Z}$ và rút gọn cơ sở bằng thuật toán LLL (`flatter`) để thu được các vector $u_i$ có độ dài nhỏ.
2. **Khôi phục khóa $sk$ và số nguyên tố $p$:**
   - Lấy 8 vector trực giao ngắn nhất và tính các giá trị $V_i = (u_i \cdot B) \pmod q$.
   - Dựng ma trận lưới Kannan CVP kích thước $9 \times 9$ ghép giữa $V_i$, modulus $q$ và trọng số $W = 2^{433}$.
   - Chạy LLL (`flatter`) trên lưới để trích xuất số nguyên tố bí mật $sk$ 128-bit.
   - Tính các giá trị $sk \cdot V_i \bmod^\pm q$ và lấy ước chung lớn nhất $\gcd$ để thu hồi số nguyên tố $p$ 520-bit.
3. **Tìm ma trận nghịch đảo trái nguyên của $A$:**
   - Tính dạng chuẩn tắc Smith của $A$ để xác nhận tính khả nghịch trái trên tập số nguyên $\mathbb{Z}$.
   - Xây dựng ma trận $L \in \mathbb{Z}^{16 \times 112}$ thỏa mãn $L \cdot A = I_{16}$.
4. **Khôi phục vector sai số riêng và vector dịch chuyển:**
   - Tính vector hội chứng sai số $E = K \cdot e = (K \cdot (sk \cdot B) \bmod^\pm q) / p$.
   - Giải phương trình nguyên $K \cdot e_0 = E$ bằng dạng Smith của $K$, kết hợp rút gọn khoảng cách để thu được vector sai số nhỏ $e_{small}$.
   - Tính vector dịch chuyển tương đương $S' = (L \cdot (sk \cdot B - p \cdot e_{small})) \pmod q$.
5. **Giải mã bản rõ flag:**
   - Tính giá trị kết hợp $val = (sk \cdot c_2 + c_1 \cdot S') \pmod q$ và lấy thặng dư đối xứng trên khoảng $[-q/2, q/2]$.
   - Khử thừa số $sk$ modulo $p$: $pt = (sk^{-1} \cdot val) \pmod p$.
   - Chuyển đổi $pt$ sang chuỗi byte ASCII để nhận flag.

---

## 🚩 Flag
`NNS{lwe,compact,broken:https://eprint.iacr.org/2017/742.pdf}`
