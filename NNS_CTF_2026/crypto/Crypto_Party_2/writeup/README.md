# Writeup: Crypto Party 2

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `500` |
| **Author** | `Unknown` |
| **Status** | `Analyzed & Solved (Local Pipeline Ready)` |

---

## 📝 Challenge Overview
Bài toán cung cấp một dịch vụ ký ECDSA trên đường cong NIST-P256 (`curves.NIST256p`) với số lần ký tối đa 6 lần (`MAX_INVITES = 6`). Khóa bí mật `secret_key` dùng để mã hóa flag qua thuật toán AES-128/256-ECB.

---

## 🔍 Vulnerability Analysis
1. **Rò rỉ cấu trúc và giảm entropy nonce $k$:**
   - Giá trị ngẫu nhiên $k$ trong mỗi lần ký được tạo bởi:
     $$k = \text{bytes\_to\_long}(\text{str}(\text{uuid.uuid4()})[:32].\text{encode}())$$
   - Chuỗi UUIDv4 cắt 32 ký tự đầu có dạng: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxx`
   - Các vị trí byte cố định:
     - Byte 8, 13, 18, 23 luôn là dấu gạch ngang `-` (ASCII `0x2d`).
     - Byte 14 luôn là ký tự phiên bản `4` (ASCII `0x34`).
     - Byte 19 luôn thuộc tập biến thể `{'8', '9', 'a', 'b'}`.
     - 26 byte còn lại là các ký tự hex ASCII (`'0'-'9'`, `'a'-'f'`) nằm trong khoảng hẹp $[48, 102]$.
   - Nonce $k$ (256-bit) chỉ có khoảng 106 bit entropy thay vì 256 bit ngẫu nhiên. Mỗi byte bị lệch tâm rõ rệt quanh giá trị trung bình $\approx 70$.
2. **Quy về Bài toán Số Ẩn (Hidden Number Problem - HNP):**
   - Đặt $k_i = \mu + \epsilon_i$ với $\mu$ là tâm kỳ vọng đã biết trước và $|\epsilon_i| \le \Delta \ll n$.
   - Phương trình chữ ký ECDSA:
     $$s_i \equiv k_i^{-1} (h_i + r_i \cdot d) \pmod n \iff k_i \equiv s_i^{-1} h_i + (s_i^{-1} r_i) \cdot d \pmod n$$
   - Thay $k_i = \mu + \epsilon_i$:
     $$d \cdot (s_i^{-1} r_i) - \epsilon_i \equiv \mu - s_i^{-1} h_i \pmod n$$
   - Với 6 chữ ký ($m = 6$), tổng lượng thông tin rò rỉ là $6 \times (256 - 106) = 900$ bit, vượt xa kích thước 256-bit của khóa bí mật $d$.
   - Dựng lưới Kannan CVP kích thước $8 \times 8$ và rút gọn bằng LLL/`flatter` sẽ khôi phục chính xác $100\%$ khóa bí mật $d$.

---

## 🎯 Solution Flow (Không dùng code)
1. **Thu thập dữ liệu từ dịch vụ mạng:**
   - Kết nối tới instance và gửi 6 tên bạn bè bất kỳ để nhận về 6 bộ chữ ký $(r_i, s_i)$ cùng bản mã AES $ct$.
2. **Mô hình hóa HNP và tâm kỳ vọng:**
   - Xây dựng vector tâm $\mu$ từ các byte cố định và kỳ vọng của ký tự hex.
   - Tính các hệ số $t_i = s_i^{-1} r_i \pmod n$ và $u_i = \mu - s_i^{-1} h_i \pmod n$.
3. **Thiết lập lưới CVP:**
   - Dựng ma trận lưới chứa các vector cơ sở thặng dư modulo $n$, vector mục tiêu và trọng số chuẩn hóa $\Delta$.
   - Chạy LLL hoặc `flatter` để tìm vector nguyên ngắn nhất.
4. **Trích xuất khóa bí mật và giải mã:**
   - Lấy giá trị $d = \text{secret\_key}$ từ tọa độ của vector nghiệm.
   - Kiểm tra $d \cdot G == Q$ hoặc thử giải mã $ct$ bằng AES-ECB với khóa $d$.
   - Khi giải mã thành công, đọc chuỗi ASCII để nhận flag.

---

## 🚩 Flag
Sẽ thu hồi trực tiếp từ instance thông qua script solver HNP CVP.
