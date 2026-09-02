# 📌 Nhật Ký Kiểm Thử & Phân Tích (Testing Log & Notes)

## 1. Quy Tắc Tổ Chức Thư Mục (Workspace Guidelines)
- **`script/`**: Thư mục workspace nháp. Toàn bộ script test, payload thử nghiệm, fuzzing, giải mã linh tinh tại đây.
- **`solver/`**: Khi script giải bài hoàn thiện và lấy được flag thành công, chuyển/lưu script chính thức vào `solver/solve.py`.
- **`writeup/`**: Thư mục viết báo cáo, phân tích kỹ thuật và ghi lại Flag sau khi giải xong bài.

---

## 2. Thông Tin Mục Tiêu & Kiến Trúc (Target Architecture)
- **Active URL:** `https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io/`
- **Reverse Proxy:** `nginx/1.30.4`
- **Backend Application:** Python (Flask / Werkzeug WSGI đơn worker)
- **Dịch vụ:** `NeuroServe — AI Inference Gateway v3.1.0` (Giao diện web ghi `v2.4.0`)
- **Yêu cầu token:** Chuỗi 48 ký tự chữ và số (`[0-9a-zA-Z]`, không có ký tự đặc biệt).

---

## 3. Nhật Ký Các Thử Nghiệm Đã Thực Hiện (Testing Records)

### A. Rà soát Endpoint & Routing (Path & Method Fuzzing)
* `GET /`: Giao diện Web xác thực Token (`HTTP 200 OK`, 5.9 KB).
* `GET /health`: Healthcheck endpoint (`HTTP 200 OK`, 47 B): `{"service":"neuroserve-gateway","status":"ok"}`.
* `GET /api/status`: Metadata hệ thống (`HTTP 200 OK`, 142 B): `{"auth":"bearer-token","service":"NeuroServe AI Inference Gateway","token_format":"48 alphanumeric characters (0-9a-zA-Z)","version":"3.1.0"}`.
* `GET /static/ctfd-theme.css`: File stylesheet giao diện (`HTTP 200 OK`, 100 KB).
* `POST /api/authenticate`: Endpoint xác thực chính (`HTTP 401 / 200`, 52 B).
* `GET /api/authenticate`: Method Not Allowed (`HTTP 405`, 153 B).
* **Các đường dẫn đã quét và xác nhận không tồn tại (`HTTP 404 Not Found`):**
  - Docs / Schemas: `/docs`, `/redoc`, `/openapi.json`, `/swagger.json`, `/api/docs`, `/api/schema`
  - Models / Inference: `/api/models`, `/api/inference`, `/api/predict`, `/api/chat`, `/api/v1/chat/completions`
  - File hệ thống & Debug: `/robots.txt`, `/sitemap.xml`, `/.git/`, `/.env`, `/Dockerfile`, `/version`

### B. Kiểm tra Header Bypasses & Overrides
* `X-Original-URL`, `X-Rewrite-URL`, `X-HTTP-Method-Override`
* `Authorization: Bearer <token>`, `Authorization: Token <token>`, `X-API-Key: <token>`
* `Accept: application/xml`, `Accept: text/plain`, `X-Debug: 1`, `X-Forwarded-For: 127.0.0.1`
* $\rightarrow$ **Kết quả:** Không có cơ chế bypass qua header.

### C. Kiểm tra Phản Hồi của Payload Xác Thực (Payload Fuzzing)
1. **Sai định dạng (Format Mismatch):** Độ dài $\neq 48$, chuỗi rỗng, chứa ký tự lạ (`!`, khoảng trắng, null byte `\x00`):
   - Phản hồi: `HTTP 401` | `{"authenticated":false,"error":"invalid token format — expected 48 alphanumeric characters"}`
2. **Đúng định dạng 48 ký tự nhưng sai giá trị:**
   - Phản hồi: `HTTP 401` | `{"authenticated":false,"error":"invalid API token"}` (Độ dài cố định 52 bytes).
3. **Type Confusion (Lỗ hổng Unhandled Exception):**
   - Gửi JSON Array `["test"]` hoặc JSON Number `12345` đến `POST /api/authenticate`:
   - Phản hồi: `HTTP 500 Internal Server Error` (Flask default unhandled exception do gọi `.get()` trên kiểu không phải `dict`).
4. **Kiểm tra 32 Semantic Prefixes:**
   - Thử các prefix: `ns`, `neuro`, `serve`, `admin`, `token`, `secret`, `key`, `flag`, `ctf`, `bearer`, `ai`, `prod`, `master`, v.v.
   - Phản hồi: 100% trả về cùng mã `401` và body 52 bytes $\rightarrow$ Token không theo từ khóa tiếng Anh dễ đoán.

### D. Cơ Chế Nghẽn Kết Nối & Nginx 502 Bad Gateway
* **Hiện tượng:** Gửi request liên tiếp $< 2.0\text{s}$ khiến Nginx trả về `502 Bad Gateway`.
* **Quan sát bổ sung:** Qua test tải, `502/503` vẫn có thể xen kẽ ở cadence $2.5 - 3.0\text{s}$; đây là trạng thái upstream/queue dao động, không phải kết quả của token.
* **Healthcheck:** Sau `502/503`, solver cooldown rồi gọi `GET /health`; chỉ tiếp tục probe `/api/authenticate` khi health trả `HTTP 200` với `status=ok` và đạt đủ 3 phản hồi `401` liên tiếp.

### E. Kiểm Định Kênh Thời Gian (Timing Side-Channel / CWE-208)
* **Kiểm định xen kẽ A/B (10 vòng lặp, 4 ký tự đại diện `a`, `0`, `A`, `Z`):**
  - Giá trị trung vị hội tụ ở $32.2\text{ms} - 33.8\text{ms}$ (chênh lệch $\sim 1.6\text{ms}$).
  - Độ lệch chuẩn do nhiễu mạng dao động $\pm 1.8\text{ms} - 2.8\text{ms}$.
  - Điểm số $t\text{-Score} \approx 1.01$ ($p > 0.05$) $\rightarrow$ Không có độ trễ nhân tạo lớn (`sleep`).
* **Đang chạy kiểm tra quét 3 vòng trên toàn bộ 62 ký tự** (`0-9`, `a-z`, `A-Z`) cho vị trí số 1 để xác định ký tự có độ lệch tiềm năng.
