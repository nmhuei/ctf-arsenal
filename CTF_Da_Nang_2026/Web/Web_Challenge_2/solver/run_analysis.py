#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

TARGET_URL = "https://70f3bf10-c5ff-406c-8bd9-c2d68d60ef12.222.255.138.122.nip.io"
TARGET_DIR = Path("/home/light/Workspace/CTF/CTF_Da_Nang_2026/Web/Web_Challenge_2")
CLAUDE_BIN = "/home/light/.local/bin/claude"

prompt = f"""
Chúng ta đang làm bài CTF: Web Challenge 2.
Target Instance URL: {TARGET_URL}

Đặc điểm ứng dụng vừa trích xuất từ server:
- Tên app: NebulaCommerce (React Server Components - RSC / Flight protocol v1.3).
- Server: Nginx + Next.js (Node.js).
- Endpoint:
  + GET /api/flight -> trả về Flight stream:
    0:I"app/_next/static/chunks/flight-runtime.js"
    1:M{{"type":"PageRoot","props":{{"title":"NebulaCommerce", ...}}}}
  + POST /api/flight (Content-Type: text/x-component) -> nhận Flight wire format và thực thi Server Action:
    0:I"app/_next/static/chunks/flight-runtime.js"
    1:M{{"action":"addToCart","payload":{{"sku":"NX-001","qty":1}}}}

Mã nguồn client runtime (flight-runtime.js):
- decode(text): phân tích dòng <rowId>:<tag><payload> với các tag I (import), M (model), T (text), E (error).
- reify(node, byId): phân giải directive {{"$ref": "<rowId>"}}.
- encodeAction(action, payload): mã hóa payload gửi lên server.

Đề bài: "You Trusted the Technology, but Did You Check What Happened Recently?"

Yêu cầu:
1. Phân tích lỗ hổng trong React Server Components (RSC) / Flight protocol deserialization (ví dụ Prototype Pollution, arbitrary module import, SSTI, hoặc deserialization gadget qua $ref / tag I / Server Actions).
2. Viết mã khai thác vào solve.py để gửi payload lên {TARGET_URL}/api/flight và lấy flag.
3. Cập nhật file README.md với phân tích chi tiết.
"""

ENV = os.environ.copy()
ENV["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:18000"
ENV["ANTHROPIC_API_KEY"] = "sk-webgpt-local"
ENV["CLAUDE_DEFAULT_MODEL"] = "claude-3-5-sonnet"
ENV["CLAUDE_CODE_MAX_CONTEXT_TOKENS"] = "200000"
ENV["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = "8192"

print("[*] Chạy Claude Code phân tích lỗ hổng RSC Flight...")
cmd = [
    CLAUDE_BIN,
    "-p", prompt,
    "--dangerously-skip-permissions",
    "--print"
]

proc = subprocess.Popen(
    cmd,
    cwd=str(TARGET_DIR),
    env=ENV,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

output_lines = []
for line in iter(proc.stdout.readline, ''):
    print(line, end='', flush=True)
    output_lines.append(line)

proc.stdout.close()
rc = proc.wait()
print(f"\n[*] Kết thúc với mã: {rc}")
