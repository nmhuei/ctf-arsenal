#!/usr/bin/env python3
"""Download the entire FirstBangla webmail mailbox and scan for bank-account clues."""
from __future__ import annotations
import html, re, sys, time
from pathlib import Path
import requests

BASE = "http://50.116.30.77:5000"
USER = "arif.khan@firstbangla.com"
PW = "knightsquad4041337@"
OUT = Path("evidence/fullmail")
OUT.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.headers["User-Agent"] = "dfir-forensics/1.0"

def login():
    r = s.get(f"{BASE}/login", timeout=20)
    m = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', r.text)
    data = {"username": USER, "email": USER, "password": PW}
    if m: data["csrf_token"] = m.group(1)
    r = s.post(f"{BASE}/login", data=data, timeout=20, allow_redirects=True)
    assert "Sign out" in r.text or "Inbox" in r.text, "login failed"
    print("[+] logged in")

def collect_links(folder):
    links = set()
    r = s.get(f"{BASE}/mail/{folder}", timeout=20)
    (OUT / f"listing_{folder}.html").write_text(r.text)
    for m in re.finditer(rf'href=["\'](/mail/{folder}/[^"\']+\.eml)["\']', r.text):
        links.add(m.group(1))
    return sorted(links)

def strip(t):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"[ \t]+", " ", html.unescape(t))

# account/bank patterns
PATTERNS = re.compile(
    r"(A/C\s*(?:no|number)?\s*[:#]?\s*[0-9\-]{6,})"
    r"|(account\s*(?:no|number|id)\s*[:#]?\s*[A-Z0-9\-]{5,})"
    r"|(IBAN\s*[:#]?\s*[A-Z]{2}[0-9A-Z]{10,})"
    r"|(SWIFT\s*[:#]?\s*[A-Z0-9]{8,11})"
    r"|(IFSC\s*[:#]?\s*[A-Z0-9]{6,})"
    r"|(beneficiary\s*[:#]?\s*[A-Za-z0-9 ./\-]{4,40})"
    r"|(\b[0-9]{4}-[0-9]{3,4}-[0-9]{3,4}-[0-9]{3,4}\b)"
    r"|(sort\s*code\s*[:#]?\s*[0-9\-]{6,})"
    r"|(routing\s*(?:no|number)?\s*[:#]?\s*[0-9]{6,})",
    re.I,
)

def main():
    login()
    hits = []
    for folder in ("inbox", "sent"):
        links = collect_links(folder)
        print(f"[+] {folder}: {len(links)} emails")
        for i, link in enumerate(links):
            try:
                r = s.get(BASE + link, timeout=20)
            except Exception as e:
                print("  err", link, e); continue
            fn = OUT / (folder + "_" + re.sub(r"[^A-Za-z0-9_.-]+", "_", link.split("/")[-1]))
            fn.write_bytes(r.content)
            txt = strip(r.text)
            for m in PATTERNS.finditer(txt):
                frag = m.group(0).strip()
                # context window
                idx = txt.find(frag)
                ctx = txt[max(0, idx-60):idx+80].strip()
                hits.append((link, frag, ctx))
            if i % 100 == 0:
                print(f"    {folder} {i}/{len(links)}")
    print("\n===== ACCOUNT-PATTERN HITS =====")
    seen = set()
    for link, frag, ctx in hits:
        key = (frag.lower())
        if key in seen: continue
        seen.add(key)
        print(f"[{link}]\n  {frag}\n  ...{ctx}...")
    Path("evidence/account_hits.txt").write_text(
        "\n".join(f"{l}\t{f}\t{c}" for l,f,c in hits))
    print(f"\n[+] total hits {len(hits)}, unique {len(seen)}")

if __name__ == "__main__":
    main()
