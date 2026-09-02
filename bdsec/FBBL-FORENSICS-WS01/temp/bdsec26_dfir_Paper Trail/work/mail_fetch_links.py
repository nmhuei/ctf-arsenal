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


def save(url: str, resp: requests.Response) -> Path:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", url.replace(BASE, "")).strip("_") or "root"
    path = EVIDENCE_DIR / f"mail_fetch_{name}.html"
    path.write_bytes(resp.content)
    return path


def main() -> None:
    s = requests.Session()
    login = s.get(f"{BASE}/login", timeout=15)
    csrf_match = TOKEN_RE.search(login.text)
    data = {"email": USERNAME, "password": PASSWORD}
    if csrf_match:
        data["csrf_token"] = next(g for g in csrf_match.groups() if g)
    s.post(f"{BASE}/login", data=data, timeout=15).raise_for_status()

    targets = set()
    for page in Path("evidence").glob("mail_search_*.html"):
        text = page.read_text(errors="replace")
        for href in LINK_RE.findall(text):
            if "/mail/" not in href or href in {"/mail/inbox", "/mail/sent"}:
                continue
            if any(k in href.lower() for k in [
                "following-up",
                "quick-question",
                "timing",
                "wallet",
                "logistics-update",
                "travel-booked",
                "director-again",
            ]):
                targets.add(urljoin(BASE, html.unescape(href)))
    for url in sorted(targets):
        for suffix in ["", "/source"]:
            full = url + suffix
            resp = s.get(full, timeout=15)
            if resp.status_code != 200:
                continue
            path = save(full, resp)
            print(path)


if __name__ == "__main__":
    main()
