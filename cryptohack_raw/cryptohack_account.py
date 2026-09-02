#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from manage_flags import (
    DEFAULT_ROOT,
    DEFAULT_STATE,
    Challenge,
    empty_state,
    get_entry,
    load_json,
    now_iso,
    resolve_challenge,
    save_json,
    scan_challenges,
)

BASE_URL = "https://cryptohack.org"
DEFAULT_SESSION = Path(".cryptohack_session.json")


def ensure_cloakbrowser():
    try:
        from cloakbrowser import launch
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Thieu dependency cloakbrowser. Hay chay: pip install -r requirements.txt"
        ) from exc
    return launch


def new_browser(headed: bool):
    launch = ensure_cloakbrowser()
    return launch(headless=not headed, humanize=True)


def new_context(browser, session_path: Path | None = None):
    kwargs: dict[str, Any] = {}
    if session_path and session_path.exists():
        kwargs["storage_state"] = str(session_path)
    return browser.new_context(**kwargs)


def save_session(context, session_path: Path) -> None:
    session_path.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(session_path))
    print(f"saved session: {session_path}")


def wait_manual(message: str) -> None:
    input(message.rstrip() + " ")


def extract_csrf(html: str) -> str:
    patterns = [
        r'_csrf_token:\s*"([^"]+)"',
        r'name=["\']_csrf_token["\']\s+value=["\']([^"\']+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    raise RuntimeError("Khong tim thay _csrf_token tren trang challenge. Session co the het han.")


def user_summary(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")
    login_links = [a.get("href") for a in soup.select("a[href]") if a.get("href") in {"/login/", "/register/"}]
    logout_links = [a.get("href") for a in soup.select("a[href]") if "logout" in (a.get("href") or "")]
    profile_links = [
        a.get("href")
        for a in soup.select("a[href]")
        if re.search(r"/user/[^/]+/?$", a.get("href") or "")
    ]
    return {
        "logged_in_guess": bool(logout_links or profile_links) and not login_links,
        "has_login_links": bool(login_links),
        "logout_links": logout_links,
        "profile_links": profile_links,
        "title": clean_title(soup.title.get_text(" ")) if soup.title else "",
        "text_hint": " ".join(text.split()[:30]),
    }


def clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def submit_flag(page, challenge: Challenge, flag: str) -> dict[str, Any]:
    page.goto(challenge_url(challenge), wait_until="networkidle", timeout=90_000)
    html = page.content()
    csrf = extract_csrf(html)
    endpoint = f"{BASE_URL}/api/submit/{challenge.data_challenge}.json"
    return page.evaluate(
        """async ({endpoint, flag, csrf}) => {
            const body = new URLSearchParams();
            body.set("flag", flag);
            body.set("_csrf_token", csrf);
            const response = await fetch(endpoint, {
                method: "POST",
                credentials: "same-origin",
                headers: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                body: body.toString()
            });
            let data;
            try {
                data = await response.json();
            } catch (err) {
                data = {raw: await response.text()};
            }
            return {status: response.status, ok: response.ok, data};
        }""",
        {"endpoint": endpoint, "flag": flag, "csrf": csrf},
    )


def challenge_url(challenge: Challenge) -> str:
    return f"{BASE_URL}/challenges/{challenge.category_slug}/"


def response_looks_correct(result: dict[str, Any]) -> bool:
    blob = json.dumps(result.get("data", {}), ensure_ascii=False).lower()
    if not result.get("ok"):
        return False
    if any(word in blob for word in ["incorrect", "invalid", "wrong", "error"]):
        return False
    return any(word in blob for word in ["correct", "congrat", "solved", "success", "flag accepted"])


def cmd_register(args: argparse.Namespace) -> int:
    browser = new_browser(headed=True)
    try:
        context = new_context(browser, args.session)
        page = context.new_page()
        page.goto(f"{BASE_URL}/register/", wait_until="networkidle", timeout=90_000)
        wait_manual("[*] Dang ky trong browser, xac minh neu can, roi bam Enter o day de luu session:")
        save_session(context, args.session)
        return 0
    finally:
        browser.close()


def cmd_login(args: argparse.Namespace) -> int:
    browser = new_browser(headed=True)
    try:
        context = new_context(browser, args.session)
        page = context.new_page()
        page.goto(f"{BASE_URL}/login/", wait_until="networkidle", timeout=90_000)
        wait_manual("[*] Dang nhap trong browser, roi bam Enter o day de luu session:")
        save_session(context, args.session)
        return 0
    finally:
        browser.close()


def cmd_check(args: argparse.Namespace) -> int:
    if not args.session.exists():
        raise SystemExit(f"Chua co session: {args.session}. Hay chay login/register truoc.")
    browser = new_browser(headed=args.headed)
    try:
        context = new_context(browser, args.session)
        page = context.new_page()
        page.goto(f"{BASE_URL}/challenges/", wait_until="networkidle", timeout=90_000)
        print(json.dumps(user_summary(page.content()), ensure_ascii=False, indent=2))
        return 0
    finally:
        browser.close()


def flags_from_state(state: dict[str, Any]) -> dict[str, str]:
    flags: dict[str, str] = {}
    for key, entry in state.get("entries", {}).items():
        flag = (entry.get("flag") or "").strip()
        if flag:
            flags[key] = flag
    return flags


def load_state(path: Path) -> dict[str, Any]:
    state = empty_state()
    state.update(load_json(path, empty_state()))
    state.setdefault("entries", {})
    return state


def submit_one(args: argparse.Namespace, challenge: Challenge, flag: str) -> dict[str, Any]:
    if not args.session.exists():
        raise SystemExit(f"Chua co session: {args.session}. Hay chay login/register truoc.")

    browser = new_browser(headed=args.headed)
    try:
        context = new_context(browser, args.session)
        page = context.new_page()
        result = submit_flag(page, challenge, flag)
        save_session(context, args.session)
        return result
    finally:
        browser.close()


def cmd_submit(args: argparse.Namespace) -> int:
    challenges = scan_challenges(args.root)
    state = load_state(args.state)
    challenge = resolve_challenge(challenges, args.query)

    flag = args.flag
    if flag is None:
        flag = state.get("entries", {}).get(challenge.key, {}).get("flag")
    if not flag:
        raise SystemExit(
            f"Chua co flag cho {challenge.key}. Truyen flag truc tiep hoac luu bang manage_flags.py set."
        )

    result = submit_one(args, challenge, flag)
    print(json.dumps({"challenge": challenge.key, "result": result}, ensure_ascii=False, indent=2))

    if args.update_local and response_looks_correct(result):
        entry = get_entry(state, challenge.key)
        entry["flag"] = flag
        entry["solved"] = True
        entry["updated_at"] = now_iso()
        state["updated_at"] = entry["updated_at"]
        save_json(args.state, state)
    return 0


def cmd_submit_solved(args: argparse.Namespace) -> int:
    if not args.yes:
        raise SystemExit("Lenh nay se gui tat ca flag da luu local. Them --yes de xac nhan.")
    if not args.session.exists():
        raise SystemExit(f"Chua co session: {args.session}. Hay chay login/register truoc.")

    challenges = scan_challenges(args.root)
    by_key = {c.key: c for c in challenges}
    state = load_state(args.state)
    queued = [(by_key[key], flag) for key, flag in flags_from_state(state).items() if key in by_key]
    if args.limit is not None:
        queued = queued[: args.limit]

    browser = new_browser(headed=args.headed)
    results = []
    try:
        context = new_context(browser, args.session)
        page = context.new_page()
        for index, (challenge, flag) in enumerate(queued, start=1):
            print(f"[{index}/{len(queued)}] submit {challenge.key}")
            result = submit_flag(page, challenge, flag)
            results.append({"challenge": challenge.key, "result": result})
            if args.delay:
                time.sleep(args.delay)
        save_session(context, args.session)
    finally:
        browser.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dang ky/dang nhap CryptoHack va submit flag bang session local."
    )
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION, help="File luu browser session.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Thu muc cryptohack_challenges.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="File flag/status local.")
    parser.add_argument("--headed", action="store_true", help="Mo browser co UI khi submit/check.")

    sub = parser.add_subparsers(dest="command", required=True)

    p_register = sub.add_parser("register", help="Mo trang dang ky, ban tu dien form, tool luu session.")
    p_register.set_defaults(func=cmd_register)

    p_login = sub.add_parser("login", help="Mo trang login, ban tu dang nhap, tool luu session.")
    p_login.set_defaults(func=cmd_login)

    p_check = sub.add_parser("check", help="Kiem tra session co ve dang login hay khong.")
    p_check.set_defaults(func=cmd_check)

    p_submit = sub.add_parser("submit", help="Submit 1 flag len account CryptoHack.")
    p_submit.add_argument("query", help="Challenge key/data_challenge/title, vi du: aes0.")
    p_submit.add_argument("flag", nargs="?", help="Flag. Neu bo trong se lay tu cryptohack_flags.json.")
    p_submit.add_argument(
        "--update-local",
        action="store_true",
        help="Neu response co ve dung, cap nhat solved trong cryptohack_flags.json.",
    )
    p_submit.set_defaults(func=cmd_submit)

    p_submit_solved = sub.add_parser("submit-solved", help="Submit tat ca flag da luu trong state local.")
    p_submit_solved.add_argument("--yes", action="store_true", help="Xac nhan gui hang loat.")
    p_submit_solved.add_argument("--limit", type=int, help="Chi gui N flag dau tien.")
    p_submit_solved.add_argument("--delay", type=float, default=0.8, help="Delay giua cac lan submit.")
    p_submit_solved.set_defaults(func=cmd_submit_solved)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
