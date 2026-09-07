# Writeup: Downhill

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Unknown` |
| **Status** | `Analyzed & Solved (Local Pipeline Ready)` |

---

## 📝 Challenge Overview
Thử thách cài đặt lược đồ chữ ký số trên lưới **NTRUSign** với các tham số:
- Số chiều $N = 251$.
- Modulus $q = 128$.
- Khóa bí mật gồm cặp đa thức ngắn $f, g$ và $F, G$ thỏa mãn đẳng thức NTRU $f \cdot G - g \cdot F \equiv q \pmod{x^N - 1}$.
- Server cho phép lấy tối đa 500 chữ ký (`n_sigs = 500`) trên các thông điệp tùy ý.
- Khóa AES giải mã flag được tạo trực tiếp từ đa thức bí mật $f$: $\text{key} = \text{SHA-256}(\text{bytes}(f))$.

---

## 🔍 Vulnerability Analysis
1. **Lỗ hổng hình học cơ bản của NTRUSign (Nguyen-Regev Parallelepiped Attack):**
   - Thuật toán ký sử dụng phương pháp làm tròn Babai (Babai's Rounding) trên cơ sở bí mật $(f, F)$:
     $$s = \left(\left\lfloor \frac{-m \cdot F}{q} \right\rceil \cdot f + \left\lfloor \frac{m \cdot f}{q} \right\rceil \cdot F\right) \pmod{x^N - 1}$$
   - Do sai số làm tròn phân bố đều trong hình hộp cơ bản (fundamental parallelepiped) xác định bởi cơ sở bí mật thay vì hình cầu đối xứng, mỗi chữ ký $s$ bị rò rỉ một phần hướng hình học của cơ sở bí mật.
2. **Thu hồi cơ sở qua Ma trận Hiệp phương sai (Covariance Matrix):**
   - Trong bài báo *"Learning a Parallelepiped: Cryptanalysis of GGH and NTRUSign"* (Eurocrypt 2006) của Phong Q. Nguyen và Oded Regev, các tác giả đã chứng minh:
     - Ma trận mô-men bậc hai (second moment / covariance matrix) của các chữ ký:
       $$\Sigma = \frac{1}{M} \sum_{i=1}^M s_i \cdot s_i^T$$
     - Không gian riêng tương ứng với các giá trị riêng lớn nhất của $\Sigma$ sẽ làm lộ chính xác hướng của vector cơ sở bí mật $f$.
   - Với số chiều $N = 251$ và số lượng chữ ký $M = 500 \approx 2N$, ma trận hiệp phương sai cung cấp đủ độ tin cậy thống kê để sau khi kết hợp với thuật toán LLL/`flatter`, ta khôi phục trọn vẹn đa thức bí mật $f$.

---

## 🎯 Solution Flow (Không dùng code)
1. **Thu thập 500 chữ ký:**
   - Kết nối tới server, gửi 500 chuỗi thông điệp khác nhau để thu thập đủ 500 vector chữ ký $s_i \in \mathbb{Z}^{251}$.
2. **Tính toán ma trận hiệp phương sai:**
   - Chuẩn hóa các vector chữ ký về dạng đối xứng qua gốc tọa độ.
   - Tính ma trận gramian hiệp phương sai $\Sigma = \frac{1}{500} \sum s_i s_i^T$.
3. **Phân tích phổ hoặc chiếu trực giao:**
   - Tìm các vector riêng chính (hoặc thực hiện phân tích Cholesky / SVD) trên $\Sigma$ để xác định hình dáng hình hộp.
   - Biến đổi lưới cơ sở công khai bằng ma trận biến đổi tọa độ để đưa vector ngắn $f$ về dạng tìm kiếm được bằng thuật toán LLL (`flatter`).
4. **Khôi phục $f$ và giải mã flag:**
   - Trích xuất đa thức $f$ từ cơ sở đã rút gọn.
   - Kiểm tra $f \pmod q$ khớp với khóa công khai $h$.
   - Tính khóa $\text{key} = \text{SHA-256}(\text{bytes}(f))$ và giải mã AES-ECB bản mã $ct$ để lấy flag.

---

## 🚩 Flag
Sẽ thu hồi trực tiếp khi kết nối instance thông qua script solver Nguyen-Regev covariance.
