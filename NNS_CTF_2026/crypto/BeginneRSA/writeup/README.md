# Writeup: BeginneRSA

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `139` |
| **Author** | `Zukane` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Bài toán cung cấp nhiều bộ khóa công khai RSA $(N_i, e_i)$ và bản mã $c_i$. Mục tiêu là thu hồi flag ban đầu.

---

## 🔍 Vulnerability Analysis
Cơ chế sinh khóa RSA tạo ra các modulus $N_i$ bằng cách lấy ngẫu nhiên các số nguyên tố từ một tập hữu hạn hoặc tái sử dụng trực tiếp số nguyên tố giữa các session. Khi hai modulus $N_1, N_2$ có chung thừa số $p$:
$$\gcd(N_1, N_2) = p > 1$$

---

## 🎯 Solution Flow (Không dùng code)
1. **Phát hiện cặp modulus phụ thuộc:**
   - Tính ước chung lớn nhất từng đôi một $\gcd(N_i, N_j)$ giữa tất cả các modulus công khai.
2. **Phân tích nhân tử:**
   - Khi $\gcd(N_i, N_j) = p > 1$, thừa số nguyên tố còn lại được xác định ngay lập tức: $q = N_i / p$.
3. **Tính khóa giải mã RSA:**
   - Tính giá trị hàm Euler $\phi(N_i) = (p - 1)(q - 1)$.
   - Tính số mũ giải mã bí mật $d = e^{-1} \pmod{\phi(N_i)}$.
4. **Giải mã bản mã:**
   - Khôi phục bản rõ $m = c_i^d \pmod{N_i}$.
   - Chuyển đổi $m$ từ số nguyên sang chuỗi byte ASCII để nhận flag.

---

## 🚩 Flag
`NSS{n3v3r_3v3r_r3u53_4_pr1m3!}`
