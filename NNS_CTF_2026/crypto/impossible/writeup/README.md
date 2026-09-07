# Writeup: impossible

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Unknown` |
| **Status** | `Solved (Verified Locally)` |

---

## 📝 Challenge Overview
Bài toán triển khai một mạch Zero-Knowledge Proof (Groth16 zk-SNARK) trên đường cong ghép cặp BLS12-381 bằng thư viện `bellman`. Mục tiêu là tạo ra một bằng chứng hợp lệ để chứng minh mệnh đề:
$$\text{CLAIM} = 1{,}000{,}000{,}000 \le \text{authorized\_balance} = 100$$
Đây là một mệnh đề sai về mặt logic, nên việc sinh bằng chứng thông thường qua mạch R1CS là bất khả thi.

---

## 🔍 Vulnerability Analysis
1. **Lộ Toxic Waste từ Trusted Setup:**
   - Trong thư mục bài toán có file `secret` chứa 2 dòng mã hóa ROT13:
     - `PRERZBAL_VQ` $\xrightarrow{\text{ROT13}}$ `CEREMONY_ID` = `3c311d9dfb7735e42643f394dc2c10af`
     - `GNH` $\xrightarrow{\text{ROT13}}$ `TAU` = `3894627051107121998319229043008213446770981528672674568925122813412699817`
   - Khóa bí mật $\tau$ (toxic waste trapdoor) của buổi lễ Trusted Setup đã bị rò rỉ hoàn toàn.
   - Hàm `derive(tau)` trong mã nguồn sinh ra tất cả các tham số bí mật của hệ thống: $\alpha, \beta, \gamma, \delta, g_1, g_2$.
2. **Giả mạo bằng chứng Groth16 (Proof Forgery):**
   - Phương trình xác thực Groth16 chuẩn:
     $$e(A, B) = e(\alpha, \beta) \cdot e\left(\sum a_i IC_i, \gamma\right) \cdot e(C, \delta)$$
   - Khi kẻ tấn công biết các tham số bí mật $(\alpha, \beta, \gamma, \delta)$, có thể chọn:
     - $A = \alpha \cdot G_1 = vk.\alpha_{G1}$
     - $B = \beta \cdot G_2 = vk.\beta_{G2}$
   - Khi đó $e(A, B) = e(\alpha, \beta)$, hai vế triệt tiêu phần tích khóa chính.
   - Phương trình còn lại:
     $$e\left(\sum a_i IC_i, \gamma\right) \cdot e(C, \delta) = 1_{G_T}$$
   - Từ đó giải trực tiếp phần tử nhóm $C \in G_1$:
     $$C = -\left(\sum a_i IC_i\right) \cdot \gamma \cdot \delta^{-1}$$
   - Bộ ba $(A, B, C)$ tạo thành một bằng chứng giả mạo hoàn hảo cho bất kỳ public input nào mà bộ xác thực sẽ chấp nhận $100\%$.

---

## 🎯 Solution Flow (Không dùng code)
1. **Giải mã tham số bí mật từ file secret:**
   - Áp dụng ROT13 để lấy chuỗi `ceremony_id` và số nguyên trường `tau`.
2. **Khôi phục các khóa Trapdoor:**
   - Chạy hàm phái sinh `derive(tau)` để thu được $\gamma$ và $\delta$ trong trường vô hướng $\mathbb{F}_r$.
3. **Tính toán bộ tích lũy đầu vào công khai:**
   - Đọc khóa xác thực `vk.bin`.
   - Tính phần tử nhóm đại diện cho public input: $acc = IC_0 + \text{CLAIM} \cdot IC_1$.
4. **Giả lập điểm chứng minh $C$:**
   - Nhân điểm $acc$ với đại lượng vô hướng $-\gamma \cdot \delta^{-1}$ trên nhóm $G_1$ để thu được $C$.
   - Gán $A = vk.\alpha_{G1}$ và $B = vk.\beta_{G2}$.
5. **Đóng gói và gửi bằng chứng:**
   - Định dạng chuỗi payload `<ceremony_id>:<proof_hex>`.
   - Khi instance mở kết nối TCP tới server từ xa, gửi payload và đọc flag phản hồi.

---

## 🚩 Flag
`NNS{1mp0ss1bl3_pr00fs_FR0M_C3r3m0NY_4sH35}`
