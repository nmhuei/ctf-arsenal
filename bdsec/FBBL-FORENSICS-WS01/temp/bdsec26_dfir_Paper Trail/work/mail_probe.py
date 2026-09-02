#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


BASE = "http://50.116.30.77:5000"
LOGIN_URL = f"{BASE}/login"
USERNAME = "arif.khan@firstbangla.com"
PASSWORD = "knightsquad4041337@"
EVIDENCE_DIR = Path("evidence")
MAX_PAGES = 20

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
TOKEN_RE = re.compile(
    r'name=["\'](?:csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)["\']'
    r'|value=["\']([^"\']+)["\'][^>]*name=["\'](?:csrf_token|csrf)["\']',
    re.I,
)
LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
ANCHOR_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
TEXT_SIGNAL_RE = re.compile(
    r"(rajesh|faisal|rpc|patel|attacker|gmail|proton|tuta|outlook|yahoo|"
    r"bdsec|flag|wallet|transfer|bangkok|golden|sukhumvit)",
    re.I,
)


def same_origin(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != urlparse(BASE).netloc:
        return False
    if parsed.path.startswith(("/logout", "/static", "/login")):
        return False
    return True


def save_response(name: str, response: requests.Response) -> Path:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "page"
    path = EVIDENCE_DIR / f"mail_{safe_name}.html"
    path.write_bytes(response.content)
    return path


def visible_lines(text: str) -> list[str]:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", "\n", text)
    text = html.unescape(text)
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def extract_csrf(page: str) -> str | None:
    match = TOKEN_RE.search(page)
    if not match:
        return None
    return html.unescape(next(group for group in match.groups() if group))


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": "ctf-mail-probe/1.0"})

    login_page = session.get(LOGIN_URL, timeout=15)
    save_response("login_fresh", login_page)
    login_page.raise_for_status()
    csrf = extract_csrf(login_page.text)

    data = {"email": USERNAME, "username": USERNAME, "password": PASSWORD}
    if csrf:
        data["csrf_token"] = csrf
        data["csrf"] = csrf

    login_resp = session.post(LOGIN_URL, data=data, timeout=15, allow_redirects=True)
    save_response("after_login", login_resp)
    login_resp.raise_for_status()

    parsed_base = urlparse(BASE)
    queue: deque[str] = deque([login_resp.url, urljoin(BASE, "/mail/sent")])
    seen: set[str] = set()
    findings: dict[str, set[str]] = {}
    snippets: list[tuple[str, str]] = []

    while queue and len(seen) < MAX_PAGES:
        url = queue.popleft()
        if url in seen or not same_origin(url):
            continue
        seen.add(url)
        response = session.get(url, timeout=15)
        response.raise_for_status()

        path_name = urlparse(url).path.strip("/").replace("/", "_") or "root"
        saved = save_response(path_name, response)
        text = response.text
        emails = set(EMAIL_RE.findall(text))
        if emails:
            findings[str(saved)] = emails

        for line in visible_lines(text):
            if TEXT_SIGNAL_RE.search(line) or EMAIL_RE.search(line):
                snippets.append((str(saved), line[:240]))

        targeted_links: list[str] = []
        for href, body in ANCHOR_RE.findall(text):
            cleaned = " ".join(visible_lines(body))
            if TEXT_SIGNAL_RE.search(cleaned):
                targeted_links.append(href)

        for href in targeted_links + LINK_RE.findall(text):
            joined = urljoin(url, html.unescape(href))
            parsed = urlparse(joined)
            if parsed.netloc != parsed_base.netloc:
                continue
            normalized = parsed._replace(fragment="").geturl()
            if normalized not in seen and len(seen) + len(queue) < MAX_PAGES:
                queue.append(normalized)

    print(f"login_final_url={login_resp.url}")
    print(f"pages_saved={len(seen)}")
    for path, emails in sorted(findings.items()):
        interesting = sorted(email for email in emails if email.lower() != USERNAME.lower())
        if interesting:
            print(f"emails {path}: {', '.join(interesting)}")
    print("signal_lines:")
    for path, line in snippets[:80]:
        print(f"{path}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
