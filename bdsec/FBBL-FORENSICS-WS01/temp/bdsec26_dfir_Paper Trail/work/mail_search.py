#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urlencode

import requests


BASE = "http://50.116.30.77:5000"
USERNAME = "arif.khan@firstbangla.com"
PASSWORD = "knightsquad4041337@"
EVIDENCE_DIR = Path("evidence")
TOKEN_RE = re.compile(
    r'name=["\'](?:csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)["\']'
    r'|value=["\']([^"\']+)["\'][^>]*name=["\'](?:csrf_token|csrf)["\']',
    re.I,
)


def save(name: str, response: requests.Response) -> None:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
    (EVIDENCE_DIR / f"mail_search_{safe}.html").write_bytes(response.content)


def token(text: str) -> str | None:
    match = TOKEN_RE.search(text)
    if not match:
        return None
    return html.unescape(next(group for group in match.groups() if group))


def strip(text: str) -> list[str]:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", "\n", text)
    return [re.sub(r"\s+", " ", html.unescape(line)).strip() for line in text.splitlines()]


def main() -> None:
    s = requests.Session()
    login = s.get(f"{BASE}/login", timeout=15)
    csrf = token(login.text)
    data = {"email": USERNAME, "password": PASSWORD}
    if csrf:
        data["csrf_token"] = csrf
    after = s.post(f"{BASE}/login", data=data, timeout=15, allow_redirects=True)
    after.raise_for_status()
    for q in [
        "Faisal",
        "user323456789",
        "travel logistics",
        "R knows my rates",
        "passport documents",
        "Rajesh Patel",
        "RPC Consulting",
        "external bank account",
        "bank account ID",
        "account ID",
        "beneficiary",
        "routing",
        "IFSC",
        "Rajesh cut",
        "clean wallet",
    ]:
        resp = s.get(f"{BASE}/search?{urlencode({'q': q})}", timeout=15)
        resp.raise_for_status()
        save(q, resp)
        print(f"query={q!r} url={resp.url} bytes={len(resp.content)}")
        for line in strip(resp.text):
            if re.search(r"faisal|user323|travel|logistics|passport|documents|telegram|handle|username", line, re.I):
                print(line[:220])


if __name__ == "__main__":
    main()
