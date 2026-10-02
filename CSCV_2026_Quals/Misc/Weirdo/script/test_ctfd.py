import urllib.request
import re
import json

url = "https://qual.cscv.vn/challenges"
cookie = "session=1519fa17-9e4d-4cfb-a628-7d44bdfcd700.HJg1u3KhZzCmYz7HgpX80UWprYk"

req = urllib.request.Request(url, headers={
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        print("Status:", resp.status)
        m = re.search(r"csrfNonce['\"]\s*:\s*['\"]([^'\"]+)", html)
        if m:
            nonce = m.group(1)
            print("csrfNonce:", nonce)
            
            # Now test submitting
            attempt_url = "https://qual.cscv.vn/api/v1/challenges/attempt"
            flag = "CSCV2026{th3_sky_1s_n0t_r34l_5acb9c6b}"
            payload = json.dumps({"challenge_id": 14, "submission": flag}).encode("utf-8")
            post_req = urllib.request.Request(attempt_url, data=payload, headers={
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "CSRF-Token": nonce
            })
            with urllib.request.urlopen(post_req) as post_resp:
                result = post_resp.read().decode("utf-8")
                print("Submit Response:", result)
        else:
            print("Nonce not found. Title:", re.findall(r"<title>.*?</title>", html))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Error body:", e.read().decode('utf-8', errors='ignore')[:300])
