#!/usr/bin/env python3
import re
import sys
from json import dumps

import requests


def bxor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def target_from_args(argv: list[str]) -> str:
    if len(argv) == 2:
        target = argv[1]
        if target.startswith(("http://", "https://")):
            return target.rstrip("/")
        return f"http://{target}".rstrip("/")
    if len(argv) == 3:
        return f"http://{argv[1]}:{argv[2]}"
    print(f"usage: {argv[0]} <URL>  OR  {argv[0]} <host> <port>")
    raise SystemExit(1)


def decode_werkzeug_cookie_value(value: str) -> str:
    """Decode the form Flask/Werkzeug uses for cookie values containing ';'.

    A token returned by set_cookie('auth', 'ct;tag') is usually stored by
    requests as '"ct\\073tag"'.  The octal escape \073 is a semicolon.
    """
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]

    # Werkzeug emits semicolon as octal \073 inside a quoted cookie value.
    # Keep this conservative: only decode escapes we need for this challenge.
    value = value.replace(r"\073", ";")
    value = value.replace(r"\054", ",")
    value = value.replace(r"\134", "\\")
    value = value.replace(r'\"', '"')
    return value


def parse_auth_cookie(raw: str) -> tuple[bytes, bytes]:
    token = decode_werkzeug_cookie_value(raw)
    parts = token.split(";")
    if len(parts) != 2:
        raise ValueError(f"expected ct;tag after cookie decoding, got {token!r}")
    ct_hex, tag_hex = parts
    return bytes.fromhex(ct_hex), bytes.fromhex(tag_hex)


def werkzeug_quote_auth(ct_hex: str, tag_hex: str) -> str:
    # Cookie header value that Flask/Werkzeug decodes back to 'ct;tag'.
    return f'"{ct_hex}\\073{tag_hex}"'


def extract_flag(text: str) -> str | None:
    for pat in [r"crypto\{[^}]+\}", r"BZHCTF\{[^}]+\}", r"[A-Za-z0-9_]+CTF\{[^}]+\}"]:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def main() -> int:
    base = target_from_args(sys.argv)
    session = requests.Session()

    # The provided app exposes this; it clears the single-user DB and rotates the key.
    try:
        session.get(f"{base}/reset-db", timeout=10)
    except requests.RequestException:
        pass

    username = "A" * 96
    password = "pw"
    data = {"username": username, "password": password}

    try:
        r = session.post(f"{base}/register", data=data, allow_redirects=False, timeout=10)
        if r.status_code == 403:
            print("[-] registration forbidden; visit /reset-db once, then rerun")
            return 2

        # Important: do not follow the redirect, or the Set-Cookie may be hidden.
        r = session.post(f"{base}/login", data=data, allow_redirects=False, timeout=10)
    except requests.RequestException as e:
        print(f"[-] connection failed: {e}")
        return 3

    raw_token = r.cookies.get("auth")
    if not raw_token:
        print("[-] did not receive auth cookie from /login")
        print(r.text[:800])
        return 4

    try:
        known_ct, _known_tag = parse_auth_cookie(raw_token)
    except Exception as e:
        print(f"[-] could not parse auth cookie: {raw_token!r} ({e})")
        return 5

    known_pt = dumps({"username": username, "role": "guest"}).encode()
    if len(known_ct) < len(known_pt):
        print("[-] ciphertext is shorter than expected; username may have been altered")
        return 6

    keystream = bxor(known_ct, known_pt)

    # verif_token ignores is_auth from decrypt(), so any 16-byte tag works.
    target_pt = dumps({"username": "", "role": "super_admin"}).encode()
    forged_ct = bxor(target_pt, keystream[: len(target_pt)])
    fake_tag_hex = "00" * 16
    forged_cookie = werkzeug_quote_auth(forged_ct.hex(), fake_tag_hex)

    try:
        r = requests.get(f"{base}/admin", headers={"Cookie": f"auth={forged_cookie}"}, timeout=10)
    except requests.RequestException as e:
        print(f"[-] /admin request failed: {e}")
        return 7

    flag = extract_flag(r.text)
    if flag:
        print(flag)
        return 0

    print("[-] forged cookie sent, but no flag pattern found. Response follows:\n")
    print(r.text[:2000])
    print("\nManual curl equivalent:")
    print(f"curl -s -H 'Cookie: auth={forged_cookie}' {base}/admin")
    return 8


if __name__ == "__main__":
    raise SystemExit(main())
