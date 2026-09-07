# Omniscient — NNS CTF 2026

| Thuộc tính | Giá trị |
|---|---|
| Thể loại | boot2root |
| Tác giả | hoover |
| Dịch vụ | `https://omniscient-d246a368af6d.chall.nnsc.tf/reqDo` |
| Mục tiêu | đọc `/root/flag.txt` |

## 1. Mental model kiến trúc

Điểm quan trọng của bài không phải là một web application thông thường. URL HTTPS chỉ là mặt ngoài của một chuỗi thành phần firmware:

```text
HTTPS :443
    → nginx reverse proxy
    → GoAhead embedded web server (nội bộ :8888)
    → CGI /reqDo (ELF AArch64)
    → dispatcher theo trường JSON td
    → shell script /etc/wifi/bumbee_hook.sh
    → lệnh chạy với quyền của CGI
```

Firmware X5-family công khai cho thấy GoAhead được khởi động với thư mục web `/etc/www`, route CGI cho các file có phần mở rộng CGI, và binary `/etc/www/reqDo` là một chương trình AArch64 có các handler như `SetApConfig`, `SetFct`, `GetDevInfo` và `GetNetworkLog`. Ở instance của challenge, reverse proxy expose handler này bằng đường dẫn một tầng `/reqDo`; không cần truy cập trực tiếp cổng 8888.

Khi nhận `POST` JSON, `reqDo` đọc `td` để chọn handler. `SetApConfig` nhận các trường cấu hình Wi-Fi, tạo command line cho script cấu hình mạng, chạy command đó bằng cơ chế kiểu `popen()`, rồi đưa stdout của command vào response CGI. Đây là cầu nối dữ liệu nguy hiểm: input HTTP không dừng ở parser JSON mà đi tiếp tới shell.

## 2. Reconnaissance

Một số dấu hiệu xác nhận mental model:

- Cổng 80 redirect sang HTTPS; cổng 443 trả header `nginx/1.22.1`.
- `POST` tới `/reqDo` với `Content-Type: application/json` được xử lý như CGI và trả `application/json`.
- Các body JSON không có handler hợp lệ thường cho response rỗng, vì vậy chỉ nhìn status `200` không đủ để kết luận exploit thành công.
- Request không phải JSON/form sai cho lỗi HTTP khác, phù hợp với một CGI tự parse POST body thay vì một REST API đầy đủ.
- Các đường dẫn kiểu `/cgi-bin/reqDo` không phải endpoint cần dùng; route thực tế ở đây là `/reqDo`.

Handler cũ của dòng ECOVACS thường được thử đầu tiên là `sc` trong `SetApConfig`. Tuy nhiên firmware mới decode các trường Wi-Fi như base64 rồi parse chúng trước khi đưa vào phần JSON nội bộ. Payload metacharacter đặt trong `sc` vì thế không còn là primitive đáng tin cậy trên firmware này. Việc bám vào tên parameter của challenge trước sẽ dẫn đến nhiều response rỗng.

## 3. Phân tích lỗ hổng

Trong `SetApConfig`, các giá trị cấu hình được ghép vào một command bằng format string. Trường `ts` được đặt vào đoạn tương đương `TS="<giá trị ts>"`, nhưng không được shell-quote hoặc kiểm tra allowlist trước khi ghép.

Vì vậy giá trị hợp lệ về mặt JSON:

```text
"; cat /root/flag.txt; #
```

đóng dấu ngoặc kép mà chương trình thêm vào, chèn một command mới, rồi dùng `#` để vô hiệu hóa phần command còn lại. Về mặt shell, cấu trúc phát sinh có dạng:

```text
TS=""; cat /root/flag.txt; # ...
```

Đây là command injection, không phải path traversal hay lỗi đọc file của nginx. Lệnh được thực thi ở phía robot trong context của CGI. Do CGI chạy với quyền root, `cat` có thể đọc file mục tiêu. Stdout được handler thu lại, nên nội dung flag xuất hiện trực tiếp trong HTTP response.

## 4. Attack flow

1. Gửi `POST /reqDo` với `Content-Type: application/json`.
2. Chọn `SetApConfig` bằng `td`.
3. Để `s`, `p`, `sc`, `sck2` và `lb` là chuỗi rỗng để không phụ thuộc vào cấu hình Wi-Fi.
4. Đặt payload command injection vào `ts`.
5. Regex nội dung response để lấy chuỗi flag.
6. Ghi flag vào `flag.txt` ở thư mục challenge.

Payload logic tối thiểu là:

```text
td      = SetApConfig
s/p/... = rỗng
ts      = "; cat /root/flag.txt; #
```

Script tái hiện đầy đủ nằm tại [`../solver/solve.py`](../solver/solve.py). Chạy từ thư mục challenge:

```bash
python3 solver/solve.py
```

Script cũng nhận `--url` để kiểm thử instance khác cùng cấu trúc và tự ghi kết quả vào `flag.txt`.

## 5. Kết quả

Flag thu được từ instance live:

```text
NNS{the_omN1scien7_X5_571ll_7ru575_ev3ry_t1M3574mP}
```

## 6. Bài học và hướng khắc phục

- Không tạo shell command bằng cách nối chuỗi từ dữ liệu HTTP. Dùng API nội bộ hoặc `execve()` với argv cố định.
- Nếu `ts` thật sự chỉ là timestamp, validate theo định dạng thời gian allowlist; không chấp nhận quote, newline hay shell metacharacter.
- Không phản chiếu stdout của command tùy ý vào HTTP response.
- CGI cấu hình mạng cần authentication/authorization và nên chạy với user có quyền tối thiểu, đặc biệt khi handler có khả năng tác động hệ thống.
- Việc base64-encode một số trường khác không phải biện pháp chống injection nếu còn một trường raw được đưa vào shell.
