#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests


BASE = "http://50.116.30.77:5000"
USERNAME = "arif.khan@firstbangla.com"
PASSWORD = "knightsquad4041337@"
OUT = Path("evidence/fullmail")
TOKEN_RE = re.compile(
    r'name=["\'](?:csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)["\']'
    r'|value=["\']([^"\']+)["\'][^>]*name=["\'](?:csrf_token|csrf)["\']',
    re.I,
)
LINK_RE = re.compile(r'href=["\']([^"\']+/mail/(?:inbox|sent)/[^"\']+\.eml)["\']|href=["\'](/mail/(?:inbox|sent)/[^"\']+\.eml)["\']', re.I)


def token(text: str) -> str | None:
    m = TOKEN_RE.search(text)
    if not m:
        return None
    return html.unescape(next(g for g in m.groups() if g))


def safe_name(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", url.replace(BASE, "")).strip("_")


def get_with_retry(s: requests.Session, url: str, **kwargs) -> requests.Response:
    last: Exception | None = None
    for attempt in range(1, 6):
        try:
            return s.get(url, timeout=kwargs.pop("timeout", 90), **kwargs)
        except requests.RequestException as exc:
            last = exc
            print(f"retry_get attempt={attempt} url={url} error={type(exc).__name__}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"failed GET {url}: {last}")


def post_with_retry(s: requests.Session, url: str, **kwargs) -> requests.Response:
    last: Exception | None = None
    for attempt in range(1, 6):
        try:
            return s.post(url, timeout=kwargs.pop("timeout", 90), **kwargs)
        except requests.RequestException as exc:
            last = exc
            print(f"retry_post attempt={attempt} url={url} error={type(exc).__name__}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"failed POST {url}: {last}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    login = get_with_retry(s, f"{BASE}/login")
    data = {"email": USERNAME, "password": PASSWORD}
    csrf = token(login.text)
    if csrf:
        data["csrf_token"] = csrf
    r = post_with_retry(s, f"{BASE}/login", data=data, allow_redirects=True)
    r.raise_for_status()

    links: set[str] = set()
    for folder in ("inbox", "sent"):
        r = get_with_retry(s, f"{BASE}/mail/{folder}")
        r.raise_for_status()
        (OUT / f"listing_{folder}.html").write_bytes(r.content)
        for groups in LINK_RE.findall(r.text):
            href = next(g for g in groups if g)
            links.add(urljoin(BASE, html.unescape(href)))

    print(f"links={len(links)}")
    count = 0
    for url in sorted(links):
        for full in (url, f"{url}/source"):
            path = OUT / f"{safe_name(full)}.html"
            if path.exists() and path.stat().st_size:
                continue
            resp = get_with_retry(s, full)
            if resp.status_code != 200:
                continue
            path.write_bytes(resp.content)
            count += 1
            if count % 100 == 0:
                print(f"fetched={count}")
            time.sleep(0.02)
    print(f"new_fetched={count}")


if __name__ == "__main__":
    main()
