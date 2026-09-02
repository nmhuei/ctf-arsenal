#!/usr/bin/env python3
import html, re, sys
import requests

BASE = "http://50.116.30.77:5000"
term = sys.argv[1]
s = requests.Session()
r = s.get(BASE + "/login", timeout=30)
m = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', r.text)
data = {"email": "arif.khan@firstbangla.com", "password": "knightsquad4041337@"}
if m:
    data["csrf_token"] = m.group(1)
s.post(BASE + "/login", data=data, timeout=30, allow_redirects=True)
r = s.get(BASE + "/search", params={"q": term}, timeout=60)
print("STATUS", r.status_code, "BYTES", len(r.content), "TERM", repr(term))
count = re.search(r'(\d+) result\(s\)', r.text)
print("COUNT", count.group(1) if count else "?")
for item in re.finditer(r'<a class="mail-row" href="([^"]+)">(.*?)</a>', r.text, re.S):
    href, block = html.unescape(item.group(1)), item.group(2)
    values = []
    for css in ("mail-person", "mail-subject", "mail-snippet", "mail-date"):
        found = re.search(rf'class="{css}"[^>]*>(.*?)</', block, re.S)
        value = re.sub(r'<[^>]+>', ' ', html.unescape(found.group(1))).strip() if found else ""
        values.append(re.sub(r'\s+', ' ', value))
    print(" | ".join((href, *values)))
