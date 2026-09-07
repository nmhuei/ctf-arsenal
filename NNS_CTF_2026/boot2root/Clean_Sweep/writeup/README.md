# Clean Sweep — Writeup

## Tổng quan

Đây là bài boot2root mô phỏng web CGI của ECOVACS DEEBOT T9 AIVI, firmware
1.4.9. Mục tiêu chạy HTTPS tại
`clean-sweep-a80a282bd7c4.chall.nnsc.tf:443`; flag nằm trong
`/root/flag.txt`.

Kết quả cuối: CGI cho phép gọi lệnh shell khi chưa xác thực. Một giá trị JSON
được dùng làm tham số Wi-Fi đã thoát khỏi dấu quote của shell, sau đó thực thi
lệnh tùy ý với quyền của tiến trình CGI (root). Lệnh đọc flag được trả lại qua
stdout của CGI và proxy HTTP.

Flag đã được lưu cục bộ tại [`../flag.txt`](../flag.txt). Flag không được gửi
đến bất kỳ nền tảng chấm thi nào.

## 1. Mô hình kiến trúc cần hình dung

Luồng xử lý của challenge có thể rút gọn như sau:

```text
HTTP client
    │ TLS :443
    ▼
Nginx / CGI adapter
    │ chuyển POST JSON vào CGI
    ▼
/etc/www/reqDo  (ELF AArch64, chạy quyền root)
    │ đọc REQUEST_METHOD, CONTENT_TYPE và body
    ▼
JSON dispatcher theo trường td
    │
    └── SetApConfig
            │ dựng command string
            ▼
          popen() → /bin/sh
            │ stdout được capture
            ▼
          HTTP response
```

Điểm dễ gây nhầm là URL nhìn giống một web server hiện đại, nhưng phần lõi là
một CGI legacy. Vì vậy cần phân biệt ba lớp:

1. Nginx chỉ là lớp TLS/proxy và có response mặc định cho nhiều URL một đoạn.
2. `reqDo` là dispatcher JSON, không phải REST API với nhiều endpoint độc lập.
3. Các thao tác Wi-Fi được thực hiện bằng shell script qua một command string,
   chứ không phải bằng API hệ điều hành an toàn.

## 2. Reconnaissance

### Bề mặt mạng và HTTP

Port 80 redirect sang HTTPS; port 443 trả lời với Nginx 1.22.1. Các port TCP
phổ biến khác không cho thấy dịch vụ hữu ích.

Một số dấu hiệu quan trọng khi thử HTTP:

| Thử nghiệm | Quan sát |
| --- | --- |
| GET `/`, `/foo`, `/reqDo` | HTTP 200, `application/json`, body rỗng |
| GET URL có nhiều segment như `/cgi-bin/` | HTTP 404 |
| POST không có body hoặc sai content type | HTTP 400/500 tùy dạng request |
| POST với `Content-Type: application/json` | được dispatcher tiếp nhận |
| OPTIONS/TRACE | không mở ra một API quản trị hữu ích |
| POST JSON tới `/reqDo`, thay `sc` bằng `sleep` | thời gian phản hồi tăng đúng theo thời gian sleep |

Các tên quen thuộc như `/cgi-bin/`, `/api/`, `/action/`, `ecovacs.cgi` và
những biến thể của `reqDo` được kiểm tra. `/reqDo` là đường dẫn dùng trong
solver. Nhiều URL một segment cùng trả body rỗng do lớp adapter có fallback
chung, nên status code riêng nó không đủ để kết luận endpoint có tồn tại.

### Lấy đúng firmware để giảm phỏng đoán

Metadata OTA công khai xác nhận class `659yh8`, platform `px30`, phiên bản
`1.4.9` và kích thước firmware 59,611,104 bytes. Firmware tải xuống có MD5
`1de7de90bf4b23b3b3162d540fad7c6a`, khớp metadata. Việc đối chiếu này giúp
tránh suy luận từ firmware Ecovacs model khác.

Sau khi giải mã và unpack filesystem, các file liên quan là:

- `/etc/rc.d/goahead.sh`: khởi động GoAhead trên cổng nội bộ 8888.
- `/etc/www/route.txt`: khai báo route CGI và action handler.
- `/etc/www/reqDo`: executable AArch64, có symbol/debug information.
- `/etc/conf/cgi.conf`: trỏ tới hook `/etc/wifi/bumbee_hook.sh`.
- `/etc/wifi/bumbee_hook.sh`: nhận các biến môi trường Wi-Fi và gọi tiếp
  `mdsctl`/các tiện ích hệ thống.

`route.txt` cũng cho thấy đây là kiến trúc GoAhead CGI legacy: các request
POST JSON được đưa vào CGI, sau đó CGI tự in HTTP header và response body.

## 3. Phân tích nguyên nhân gốc

### Dispatcher JSON

Hàm chính của `reqDo` chỉ chấp nhận phương thức POST và kiểm tra
`CONTENT_TYPE` có chứa `application/json`. Body được parse thành object; trường
`td` chọn một trong các nhánh như `GetDevInfo`, `GetCredential`,
`GetNetworkLog`, `SetFct` và `SetApConfig`.

Không có lớp xác thực hiệu quả trước dispatcher trong instance. File
`auth.txt` tồn tại trong firmware, nhưng request khai thác vẫn đi thẳng vào
CGI mà không cần credential.

### Nhánh SetApConfig

Nhánh này lấy các trường `s`, `p`, `sc`, `sck2` và `lb` từ JSON.

| Trường | Cách được dùng |
| --- | --- |
| `s`, `p` | được base64-encode trước khi đưa vào command |
| `sc`, `sck2`, `lb` | được chèn trực tiếp vào chuỗi command |
| `td` | quyết định nhánh dispatcher, không phải dữ liệu command tùy ý |

Binary dựng một command có cấu trúc tương đương:

```text
td="SetApConfig" SSID="..." PASSPHRASE="..." sc="..." sck2="..." lb="..." /etc/wifi/bumbee_hook.sh
```

Sau đó command được đưa cho `popen()`; trên Linux, `popen()` sử dụng shell để
phân tích chuỗi. Giá trị `sc` không được quote/escape theo ngữ cảnh shell.
Do đó attacker có thể đóng dấu quote của `sc`, chèn dấu `;`, chạy lệnh mới,
rồi dùng `#` để bỏ qua phần còn lại của command.

Đây là command injection, không phải buffer overflow. Kích thước các buffer
chỉ giới hạn độ dài output; nó không loại bỏ metacharacter của shell. Vì CGI
chạy bằng root, primitive này trực tiếp trở thành arbitrary command execution
và đọc được file root.

### Kênh trả kết quả

`cmd_system()` mở pipe bằng `popen`, đọc stdout vào buffer và thêm NUL kết
thúc. Nhánh `SetApConfig` in buffer này ra stdout trước khi CGI kết thúc.
Adapter chuyển stdout đó thành body HTTP. Đây là lý do payload đọc file không
cần out-of-band channel hay timing oracle.

## 4. Attack flow

1. Gửi POST tới `/reqDo` với `Content-Type: application/json`.
2. Chọn dispatcher `SetApConfig` bằng `td`.
3. Để `s` và `p` rỗng vì hai trường này được encode; để các trường khác không
   cần thiết ở giá trị rỗng.
4. Đặt `sc` thành dữ liệu có dạng “đóng quote → nối command → comment”.
5. Trước khi đọc flag, xác minh primitive bằng một marker `printf` và một
   payload `sleep`; response marker và độ trễ đều xuất hiện đúng như dự đoán.
6. Thay command bằng thao tác đọc `/root/flag.txt`. Nội dung flag xuất hiện
   trong HTTP body, kèm newline/CRLF của CGI.
7. Solver lọc flag theo mẫu `NNS{...}`, ghi đúng một dòng vào `flag.txt` trong
   thư mục challenge.

Solver reproducible nằm tại [`../solver/solve.py`](../solver/solve.py). Chạy:

```text
python3 solver/solve.py
```

Có thể đổi target bằng biến môi trường `CLEAN_SWEEP_URL`; mặc định script dùng
đúng instance của challenge. Script chỉ thực hiện một request POST hẹp, không
fuzz và không có logic submit flag.

## 5. Kiểm chứng

Các kiểm tra đã thực hiện:

- Test helper theo TDD: ban đầu fail khi solver chưa có API; sau triển khai,
  `python3 -m pytest -q script/test_solve.py` cho `2 passed`.
- `python3 -m py_compile solver/solve.py` thành công.
- Request live với marker trả marker qua HTTP.
- Request live với `sleep 2` tăng thời gian phản hồi khoảng hai giây.
- Request live đọc `/root/flag.txt` trả đúng một flag duy nhất.
- Chạy lại solver sau khi tạo file local và kiểm tra nội dung `flag.txt` khớp
  response live.

## 6. Cách khắc phục

- Không ghép dữ liệu người dùng vào shell command. Nếu bắt buộc gọi tiến
  trình, dùng `execve`/API process với argv tách biệt và allow-list giá trị.
- Nếu cần giữ hook script, truyền dữ liệu qua file/IPC có format an toàn;
  script cũng phải quote biến đúng chuẩn shell.
- Đặt authentication/authorization ở trước CGI, không dựa vào route mặc định.
- Chạy CGI bằng user đặc quyền tối thiểu; không để endpoint Wi-Fi có quyền
  root nếu không cần.
- Ghi log và kiểm thử regression với quote, semicolon, command substitution,
  newline và các shell metacharacter.
