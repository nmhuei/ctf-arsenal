#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


BASE = "http://50.116.30.77:5000"
USERNAME = "arif.khan@firstbangla.com"
PASSWORD = "knightsquad4041337@"
EVIDENCE_DIR = Path("evidence")
TOKEN_RE = re.compile(
    r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']'
    r'|value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token["\']',
    re.I,
)
LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)


def safe_path(url: str) -> Path:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", url.replace(BASE, "")).strip("_")
    return EVIDENCE_DIR / f"mail_payment_{name}.html"


def main() -> None:
    session = requests.Session()
    login = session.get(f"{BASE}/login", timeout=15)
    login.raise_for_status()
    csrf_match = TOKEN_RE.search(login.text)
    data = {"email": USERNAME, "password": PASSWORD}
    if csrf_match:
        data["csrf_token"] = next(group for group in csrf_match.groups() if group)
    session.post(f"{BASE}/login", data=data, timeout=15).raise_for_status()

    targets: set[str] = set()
    for page in EVIDENCE_DIR.glob("mail*.html"):
        text = page.read_text(errors="replace")
        for href in LINK_RE.findall(text):
            href = html.unescape(href)
            if "/mail/" in href and "payment-processed" in href.lower():
                targets.add(urljoin(BASE, href))

    for url in sorted(targets):
        for full in (url, f"{url}/source"):
            resp = session.get(full, timeout=15)
            if resp.status_code != 200:
                continue
            path = safe_path(full)
            path.write_bytes(resp.content)
            print(path)


if __name__ == "__main__":
    main()
