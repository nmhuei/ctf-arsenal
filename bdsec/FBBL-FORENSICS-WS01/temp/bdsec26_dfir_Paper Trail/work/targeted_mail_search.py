#!/usr/bin/env python3
import html, re, time
import requests

BASE = "http://50.116.30.77:5000"
USER = "arif.khan@firstbangla.com"
PASSWORD = "knightsquad4041337@"
TERMS = [
    "Rajesh Patel", "RPC Consulting", "bank details", "account number",
    "beneficiary", "IFSC", "SWIFT", "wire instructions",
    "payment instructions", "secure transfer method", "external bank",
    "bank account ID", "settlement account", "receiving account",
    "commission", "consulting fee", "remittance"
]

session = requests.Session()
login = session.get(BASE + "/login", timeout=20)
match = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', login.text)
data = {"email": USER, "password": PASSWORD}
if match:
    data["csrf_token"] = match.group(1)
resp = session.post(BASE + "/login", data=data, timeout=30, allow_redirects=True)
print("LOGIN", resp.status_code, resp.url)

for term in TERMS:
    resp = session.get(BASE + "/search", params={"q": term}, timeout=30)
    count = re.search(r'(\d+) result\(s\)', resp.text)
    rows = []
    for item in re.finditer(r'<a class="mail-row" href="([^"]+)">(.*?)</a>', resp.text, re.S):
        href, block = html.unescape(item.group(1)), item.group(2)
        values = []
        for css in ("mail-person", "mail-subject", "mail-snippet", "mail-date"):
            found = re.search(rf'class="{css}"[^>]*>(.*?)</', block, re.S)
            value = re.sub(r'<[^>]+>', ' ', html.unescape(found.group(1))).strip() if found else ""
            values.append(re.sub(r'\s+', ' ', value))
        rows.append((href, *values))
    print(f"\nTERM {term!r} status={resp.status_code} count={count.group(1) if count else '?'} rows={len(rows)}")
    for row in rows[:15]:
        print(" | ".join(row))
    time.sleep(1.5)
