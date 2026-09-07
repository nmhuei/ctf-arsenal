# Writeup: From Nothing

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Zukane` |
| **Status** | `Solved` |

---

## 📝 Challenge Overview
Thử thách định nghĩa một đường cong siêu elliptic (Hyperelliptic curve) genus-5 trên trường hữu hạn $\mathbb{F}_p$ với $p \equiv 1 \pmod{11}$ và $p \approx 2^{512}$:
$$H: v^2 + v = x^{11}$$
Khóa bí mật $e$ là hệ số tự do $e = D_v[0]$ của đa thức biểu diễn Mumford thứ hai $D = (D_u, D_v)$ trên Jacobian $J(\mathbb{F}_p)$.
Bản rõ flag được nhúng vào một điểm $P$ qua phép nâng $P = H.\text{lift\_x}(\text{flag})$, và bản mã là một divisor $ct = e \cdot J(P)$. Đề bài công khai $D_u(x)$ và tọa độ Mumford $(u, v)$ của $ct$, nhưng giấu $D_v(x)$ và $e$.

---

## 🔍 Vulnerability Analysis
1. **Không gian ứng viên khóa bí mật $e$ cực nhỏ:**
   - Theo định nghĩa tọa độ Mumford, đa thức $D_v(x)$ thỏa mãn phương trình đồng dư:
     $$D_v(x)^2 + D_v(x) \equiv x^{11} \pmod{D_u(x)}$$
   - Đa thức bậc 5 $D_u(x)$ có thể phân tích thành tích của 3 thừa số bất khả quy trên $\mathbb{F}_p$.
   - Bằng cách giải phương trình bậc hai trên từng trường thương $\mathbb{F}_p[x] / (f_i(x))$ và áp dụng Định lý Thặng dư Trung Hoa cho đa thức, ta tìm được chính xác $2^3 = 8$ đa thức ứng viên cho $D_v(x)$. Từ đó chỉ có tối đa 8 giá trị khả dĩ cho khóa $e = D_v[0]$.
2. **Tính toán chính xác bậc Jacobian qua phân rã CM Stickelberger:**
   - Để giải mã $J(P) = e^{-1} \cdot ct$, cần biết bậc của Jacobian $\#J(\mathbb{F}_p)$.
   - Đường cong $v^2 + v = x^{11}$ có tính chất nhân phức (Complex Multiplication - CM) bởi vành số nguyên của trường cyclotomic $\mathbb{Q}(\zeta_{11})$.
   - Các giá trị riêng Frobenius tương ứng với các tổng Jacobi (Jacobi sums) trong $\mathbb{Z}[\zeta_{11}]$. Do $\mathbb{Z}[\zeta_{11}]$ là vành PID (class number $h = 1$), số nguyên tố $p \equiv 1 \pmod{11}$ phân rã hoàn toàn thành tích của 10 ideal nguyên tố chính. Định lý Stickelberger cho phép xác định chính xác các giá trị riêng Frobenius mà không cần đếm điểm trên đường cong.
   - Bậc nhóm Jacobian được tính qua đa thức đặc trưng Frobenius: $\#J(\mathbb{F}_p) = \prod_{j=1}^{10} (1 - \pi_j)$.

---

## 🎯 Solution Flow (Không dùng code)
1. **Thu hồi danh sách ứng viên khóa $e$:**
   - Phân tích đa thức $D_u(x)$ thành các nhân tử bất khả quy trên $\mathbb{F}_p$.
   - Khai căn bậc hai trong từng trường mở rộng tương ứng để tìm các nghiệm thành phần của $v^2 + v - x^{11} = 0$.
   - Dùng CRT đa thức ghép lại để thu về đúng 8 đa thức $D_v(x)$ và trích xuất 8 giá trị số nguyên $e = D_v[0]$.
2. **Xác định bậc nhóm Jacobian $\#J(\mathbb{F}_p)$:**
   - Xây dựng trường cyclotomic bậc 11 $\mathbb{Q}(\zeta_{11})$.
   - Phân tích số nguyên tố $p$ trong $\mathbb{Z}[\zeta_{11}]$ để thu hồi phần tử Frobenius sinh ideal thỏa mãn điều kiện chuẩn hóa Stickelberger.
   - Tính toán 10 giá trị riêng Frobenius và tích hợp lại để tính chính xác bậc nhóm nguyên $\#J(\mathbb{F}_p)$ (khoảng 2560 bit).
3. **Phép chia vô hướng trên Jacobian:**
   - Với mỗi ứng viên trong 8 giá trị của $e$:
     - Tính nghịch đảo số học $d = e^{-1} \pmod{\#J(\mathbb{F}_p)}$.
     - Thực hiện phép nhân vô hướng $P_{cand} = d \cdot ct$ trên Jacobian $J(\mathbb{F}_p)$.
     - Kiểm tra nếu đa thức Mumford thứ nhất của điểm $P_{cand}$ có dạng bậc 1: $u(x) = x - x_0$.
4. **Trích xuất flag:**
   - Khi tìm được $u(x) = x - x_0$, chuyển đổi hoành độ $x_0 \in \mathbb{F}_p$ sang chuỗi byte để nhận flag hợp lệ.

---

## 🚩 Flag
`NNS{4nd_th3_g1ft3d_c4n_m4k3_s0m3th1ng_fr0m_n0th1ng}`
