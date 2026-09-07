# Writeup: EC PZ

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Zukane` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Bài toán cung cấp tọa độ của 3 điểm liên tiếp trong phép nhân đôi trên đường cong Elliptic $y^2 = x^3 + ax + b \pmod p$:
- $P = (x_1, y_1)$
- $Q = 2P = (x_2, y_2)$
- $R = 2Q = (x_3, y_3)$
Và điểm mã hóa $C = k \cdot F$, trong đó $F.x = \text{bytes\_to\_long}(flag)$ và số nhân $k = \text{next\_prime}(0x133713371337)$.
Các tham số trường và đường cong $(p, a, b)$ đều bị ẩn.

---

## 🔍 Vulnerability Analysis
1. **Khôi phục tham số đường cong từ điểm nhân đôi:**
   - Từ công thức nhân đôi điểm chuẩn Weierstrass:
     $$\lambda_1 = \frac{3x_1^2 + a}{2y_1} \pmod p \implies (2y_1)^2 (x_2 + 2x_1) - (3x_1^2 + a)^2 \equiv 0 \pmod p$$
   - Tương tự với bước nhân đôi $Q \to R = 2Q$:
     $$\lambda_2 = \frac{3x_2^2 + a}{2y_2} \pmod p \implies (2y_2)^2 (x_3 + 2x_2) - (3x_2^2 + a)^2 \equiv 0 \pmod p$$
   - Cả hai biểu thức đều tuyến tính theo tham số $a$ (hoặc bậc hai theo $a$). Bằng cách khử biến $a$ từ 2 quan hệ đại số trên và kết hợp phương trình đường cong $y^2 \equiv x^3 + ax + b$, ta thu được một đa thức nguyên triệt tiêu modulo $p$.
   - Lấy $\gcd$ của các đa thức sai phân nguyên suy ra giá trị số nguyên tố $p$.
2. **Khôi phục bản rõ điểm $F$:**
   - Vì $k$ là một số nguyên công khai nhỏ ($k \approx 0x133713371337$), phép nghịch đảo số nhân trên nhóm điểm đường cong $E(\mathbb{F}_p)$ khả thi ngay sau khi biết bậc nhóm:
     $$F = k^{-1} \cdot C \in E(\mathbb{F}_p)$$

---

## 🎯 Solution Flow (Không dùng code)
1. **Đồng nhất thức đại số khử tham số:**
   - Thiết lập các phương trình ràng buộc tọa độ giữa $(P, Q)$ và $(Q, R)$ theo công thức tiếp tuyến doubling.
   - Biểu diễn $a$ theo tọa độ và triệt tiêu để tìm đa thức chứa bội của $p$ trong tập số nguyên $\mathbb{Z}$.
2. **Tìm số nguyên tố $p$ và tham số $(a, b)$:**
   - Tính $\gcd$ giữa các biểu thức đại số trên $\mathbb{Z}$ để cô lập số nguyên tố $p$ 256-bit.
   - Thay $p$ vào hệ phương trình đường cong để tính chính xác $a \pmod p$ và $b \pmod p$.
3. **Giải mã điểm elliptic và flag:**
   - Khởi tạo đường cong $E = \text{EllipticCurve}(\mathbb{F}_p, [a, b])$.
   - Tính bậc của nhóm điểm $\#E(\mathbb{F}_p)$.
   - Tính nghịch đảo modulo bậc nhóm: $k_{inv} = k^{-1} \pmod{\#E}$.
   - Giải mã điểm $F = k_{inv} \cdot C$.
   - Lấy hoành độ $x_F$ của điểm $F$ và chuyển đổi thành chuỗi byte ASCII để thu được flag.

---

## 🚩 Flag
`NNS{2_EC_f0r_u_1_gu355}`
