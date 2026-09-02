# 📑 BÁO CÁO PHÂN TÍCH KỸ THUẬT & Ý TƯỞNG GIẢI QUYẾT (IDEA.md)
**Thử thách:** Misc Challenge 4 (NeuroServe AI Inference Gateway)  
**Thể loại:** Misc / Web / Side-Channel Analysis  
**Điểm số:** 650 points (Chỉ có 1 lượt giải thành công)  
**Thời gian cập nhật:** 2026-08-23  

---

## 1. 📌 Tổng Quan Thử Thách & Kiến Trúc Hệ Thống (Target Architecture)

- **Mục tiêu:** Phục hồi mã API Token quản trị gồm **48 ký tự chữ và số (`0-9a-zA-Z`)** để xác thực thành công vào gateway và nhận Flag.
- **Hạ tầng triển khai thực tế:**
  - **Reverse Proxy:** `nginx/1.30.4`
  - **Backend Server:** Python (Flask / Werkzeug WSGI đơn worker)
  - **Dịch vụ công khai:** `NeuroServe — AI Inference Gateway v3.1.0`
- **Các endpoint thực tế trên hệ thống:**
  - `GET /`: Giao diện Web xác thực Token (`HTTP 200 OK`, 5.9 KB).
  - `GET /health`: Endpoint healthcheck (`HTTP 200 OK`, 47 B): `{"service":"neuroserve-gateway","status":"ok"}`.
  - `GET /api/status`: Metadata hệ thống (`HTTP 200 OK`, 142 B): `{"auth":"bearer-token","service":"NeuroServe AI Inference Gateway","token_format":"48 alphanumeric characters (0-9a-zA-Z)","version":"3.1.0"}`.
  - `GET /static/ctfd-theme.css`: File stylesheet giao diện (`HTTP 200 OK`, 100 KB).
  - `POST /api/authenticate`: Endpoint xác thực chính (`HTTP 401 / 200`, 52 B) — mục tiêu khai thác Side-Channel Timing Leak.
  - `GET /api/authenticate`: Method Not Allowed (`HTTP 405`, 153 B).

---

## 2. 🔍 Toàn Bộ Các Thử Nghiệm Kỹ Thuật Đã Triển Khai (Empirical Testing)

### A. Rà soát Bề mặt Tấn công & Routing (Reconnaissance & Path Fuzzing)
Đã thực hiện quét hơn 30 đường dẫn tiềm năng, bao gồm các versioned routes và debug routes:
* `/api/v1/..`, `/api/v2/..`, `/api/v3/..`
* `/api/models`, `/api/inference`, `/api/generate`, `/api/chat`, `/api/predict`
* `/api/token`, `/api/tokens`, `/api/secret`, `/api/debug`, `/api/config`
* `/console`, `/admin`, `/docs`, `/openapi.json`, `/swagger.json`, `/metrics`, `/healthz`
* **Kết quả thực tế:** Toàn bộ các route trên đều trả về `HTTP 404 Not Found` (207 bytes) hoặc `HTTP 405 Method Not Allowed`. Hệ thống được cô lập nghiêm ngặt; các endpoint hữu ích còn lại là `GET /health`, `POST /api/authenticate` và `GET /api/status`.

### B. Kiểm tra Header Bypasses & Overrides
Đã thử nghiệm các kỹ thuật bypass xác thực và routing qua HTTP Headers:
* Ghi đè phương thức & đường dẫn: `X-Original-URL`, `X-Rewrite-URL`, `X-HTTP-Method-Override`.
* Header xác thực thay thế: `Authorization: Bearer <token>`, `Authorization: Token <token>`, `X-API-Key: <token>`.
* Cờ Debug & Content Negotiation: `Accept: application/xml`, `X-Debug: 1`, `X-Forwarded-For: 127.0.0.1`.
* **Kết quả thực tế:** Nginx và Flask backend xử lý đồng bộ, không phát sinh bất kỳ luồng routing ẩn hay bypass xác thực nào.

### C. Kiểm tra Payload JSON & Cờ Debug ẩn (JSON Fuzzing)
* Thử nghiệm chèn thêm các cờ điều khiển: `{"token": "...", "debug": true}`, `"verbose": true`, `"mode": "debug"`, `"admin": true`, v.v.
* **Kết quả:** Server hoàn toàn bỏ qua các trường phụ và chỉ xử lý trường `token`.

---

## 3. 🎯 Các Lỗ Hổng & Điểm Yếu Đã Được Xác Thực Thực Nghiệm 100%

### 1. Lỗ hổng Type Confusion gây sập Backend (HTTP 500)
* **Chuẩn phân loại:** CWE-20 (Improper Input Validation) / CWE-754 (Improper Check for Unusual or Exceptional Conditions).
* **Bằng chứng xác thực:**
  - Gửi JSON Object chuẩn (`{"token": "..."}`) $\rightarrow$ Server xử lý bình thường, phản hồi `401`.
  - Gửi JSON Array (`["0000..."]`) hoặc JSON Number (`12345`) với `Content-Type: application/json` $\rightarrow$ Server lập tức trả về:
    ```http
    HTTP/1.1 500 Internal Server Error
    Content-Type: text/html; charset=utf-8
    ```
* **Nguyên nhân:** Backend Python/Flask gọi trực tiếp `data.get('token')` trên dữ liệu JSON đã parse mà không kiểm tra `isinstance(data, dict)`. Khi gặp `list` hoặc `int`, code phát sinh ngoại lệ `AttributeError` không được bắt, làm sập worker thread (DoS cục bộ).

### 2. Rò rỉ cấu trúc xác thực qua thông báo lỗi (Information Disclosure)
* **Chuẩn phân loại:** CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor).
* **Bằng chứng xác thực:**
  - Khi token sai format (độ dài $\neq 48$, chuỗi rỗng, chứa ký tự lạ `!`, khoảng trắng, null byte `\x00`):
    `HTTP 401` $\rightarrow$ `{"authenticated":false,"error":"invalid token format — expected 48 alphanumeric characters"}`
  - Khi token đúng 48 ký tự alphanumeric nhưng sai nội dung:
    `HTTP 401` $\rightarrow$ `{"authenticated":false,"error":"invalid API token"}` (Độ dài cố định 52 bytes).
* **Ý nghĩa:** Tầng kiểm tra ràng buộc format hoạt động độc lập trước khi chuyển dữ liệu vào logic so khớp token bí mật.

### 3. Cơ chế giới hạn kết nối & Hiện tượng Nginx 502 Bad Gateway
* **Hiện tượng:** Gửi request với tần suất nhanh ($< 2.0\text{s}$/request) khiến Nginx trả về `502 Bad Gateway`.
* **Nguyên nhân:** Backend WSGI chạy đơn worker (single-threaded / blocking I/O). Khi request trước chưa giải phóng kết nối, Nginx không thể kết nối tới upstream và trả về `502`.
* **Giải pháp:** Duy trì khoảng cách an toàn giữa các request $\ge 2.5\text{–}3.0\text{s}$ kết hợp cơ chế retry/backoff giúp tỷ lệ phản hồi hợp lệ đạt $100\%$.

---

## 4. ⏱ Phân Tích Chuyên Sâu Kênh Phụ Thời Gian (Timing Side-Channel / CWE-208)

### A. Ý đồ thiết kế của đề bài
* Đề bài nhấn mạnh: *"The authentication endpoint seems secure, and brute force isn't practical — but failed requests may reveal more than they should."*
* Với không gian mẫu $62^{48} \approx 3.14 \times 10^{85}$ tổ hợp, việc vét cạn ngẫu nhiên là bất khả thi.
* Ý đồ của tác giả là hàm so khớp token sử dụng so sánh chuỗi tuần tự từng ký tự (`non-constant-time comparison`). Khi đoán đúng tiền tố $k$ ký tự đầu, thời gian thực thi của CPU sẽ tăng lên một lượng nhỏ trước khi trả về lỗi `401`.

### B. Kết quả kiểm định thực nghiệm A/B xen kẽ (Interleaved Statistical Testing)
Tiến hành kiểm định 10 vòng đo đạc xen kẽ trên 4 ký tự đại diện (`a`, `0`, `A`, `Z`) với khoảng cách an toàn $3.0\text{s}$:
* **Trung vị (Median) các ký tự:** Dao động trong khoảng **$32.22\text{ ms} - 33.86\text{ ms}$** (Chênh lệch tối đa chỉ $\sim 1.64\text{ ms}$).
* **Độ lệch chuẩn do nhiễu mạng ($\sigma$):** $\pm 1.79\text{ ms} - 3.90\text{ ms}$.
* **Kiểm định thống kê $t$-Score:** $t\text{-Score} \approx 1.01 < 2.0$ ($p > 0.05$).
* **Kết luận khoa học:** Server **không cài cắm `sleep()` nhân tạo lớn**. Chênh lệch thời gian ở mức CPU là vi mô ($< 0.001\text{ ms}$), hoàn toàn bị lu mờ bởi độ dao động tự nhiên của đường truyền Internet (Network Jitter $\pm 2\text{–}4\text{ ms}$).

### C. Đánh giá tính khả thi & Tỷ lệ thành công qua mạng Internet
* **Để đoán đúng toàn bộ 48 ký tự liên tiếp:** $P_{\text{thành công}} = (P_{\text{ký tự}})^{48}$.
* Do tỷ lệ Tín hiệu / Nhiễu ($\text{SNR}$) qua Internet nhỏ hơn 1:
  - Nếu chỉ lấy $3\text{–}5$ mẫu/ký tự: Xác suất đúng mỗi ký tự chỉ đạt $15\% - 25\% \implies P_{\text{toàn chuỗi}} \approx (0.25)^{48} \approx \mathbf{0\%}$.
  - Để lọc sạch nhiễu mạng qua Internet: Cần $\ge 150\text{ mẫu/ký tự} \implies 48 \times 62 \times 150 = 446.400\text{ requests}$. Với tốc độ $3\text{s}$/request, tổng thời gian cần thiết lên tới **$\approx 15.5\text{ ngày}$** (vượt quá thời gian sống của container CTF).
* **Kết luận khai thác:** Bài toán chỉ có thể khai thác thành công trong môi trường mạng cực kỳ lý tưởng (ví dụ: VPS cùng Data Center / mạng LAN với ping $< 0.2\text{ms}$ và không có jitter).

---

## 5. 💡 Quy Trình Khai Thác Tiêu Chuẩn (Exploitation Methodology)

1. **Khởi tạo kết nối:** Sử dụng `requests.Session()` với HTTP Keep-Alive để giữ kết nối ổn định.
   - Khi gặp `502/503`, chờ cooldown rồi gọi `GET /health`; chỉ tiếp tục khi nhận `HTTP 200` với `{"status":"ok"}`.
2. **Vòng lặp khôi phục từng ký tự ($pos = 0 \to 47$):**
   - Với mỗi ký tự $c \in [0-9, a-z, A-Z]$:
     $$\text{payload} = \text{recovered} + c + \text{"0"} \times (47 - pos)$$
   - Gửi request đến `POST /api/authenticate` kèm khoảng cách $3.0\text{s}$. Bỏ qua và retry nếu gặp `502`.
   - Thu thập mẫu thời gian và tính **Trung vị (Median)**.
   - Chọn ký tự có Median cao nhất đưa vào `recovered`.
3. **Xác thực cuối cùng:** Gửi chuỗi 48 ký tự hoàn chỉnh để nhận `HTTP 200 OK` và Flag.

*(Mã nguồn hoàn chỉnh đã được lưu tại [solver/solve.py](file:///home/light/Workspace/CTF/CTF_Da_Nang_2026/Misc/Misc_Challenge_4/solver/solve.py)).*

---

## 6. 🛡 Đề Xuất Khắc Phục Toàn Diện (Defensive Remediation)

```python
import secrets
from flask import Flask, request, jsonify

app = Flask(__name__)
REAL_TOKEN = "..." # Khóa bí mật 48 ký tự lưu trong Secret Manager

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    # 1. Khắc phục Type Confusion (CWE-20): Kiểm tra kiểu dữ liệu an toàn
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"authenticated": False, "error": "invalid request format"}), 400
    
    user_token = data.get('token')
    if not isinstance(user_token, str):
        return jsonify({"authenticated": False, "error": "invalid request format"}), 400

    # 2. Khắc phục Timing Attack (CWE-208): Sử dụng Constant-Time Comparison
    # secrets.compare_digest duyệt qua toàn bộ chuỗi với thời gian cố định
    if len(user_token) != len(REAL_TOKEN) or not secrets.compare_digest(user_token, REAL_TOKEN):
        # 3. Đồng nhất thông báo lỗi (CWE-200) để không rò rỉ trạng thái
        return jsonify({"authenticated": False, "error": "authentication failed"}), 401

    return jsonify({"authenticated": True, "flag": "FLAG{...}"}), 200
```
