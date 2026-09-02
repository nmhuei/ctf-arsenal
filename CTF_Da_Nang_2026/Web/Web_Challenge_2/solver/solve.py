#!/usr/bin/env python3
import argparse
import re
import sys
from urllib.parse import urljoin
import requests


def request(session, url, **kwargs):
    try:
        response = session.request(
            kwargs.pop("method", "GET"),
            url,
            timeout=kwargs.pop("timeout", 8),
            allow_redirects=False,
            **kwargs,
        )
        return response
    except requests.RequestException as exc:
        print(f"[-] {url}: {exc}")
        return None


def fingerprint_ctfd(session, base):
    print("[*] Fingerprinting CTFd")

    candidates = [
        "/",
        "/login",
        "/api/v1/config",
        "/api/v1/challenges",
    ]

    for path in candidates:
        url = urljoin(base, path)
        response = request(session, url)
        if response is None:
            continue

        print(f"[+] {response.status_code} {path}")

        version = re.search(
            r"CTFd[^0-9]*([0-9]+\.[0-9]+\.[0-9]+)",
            response.text,
            re.I,
        )
        if version:
            print(f"[+] CTFd version candidate: {version.group(1)}")

        powered_by = response.headers.get("X-Powered-By")
        if powered_by:
            print(f"[+] X-Powered-By: {powered_by}")


def test_host_header(session, base, canary):
    print("[*] Testing Host-header trust")

    url = urljoin(base, "/")
    response = request(
        session,
        url,
        headers={"Host": canary},
    )

    if response is None:
        return False

    locations = [
        response.headers.get("Location", ""),
        response.headers.get("Content-Location", ""),
        response.text,
    ]

    if any(canary in value for value in locations):
        print("[+] Host header is reflected/used")
        print("[+] Candidate: CVE-2025-23001")
        return True

    print("[-] No obvious Host-header reflection")
    return False


def test_reset_endpoint(session, base, canary):
    print("[*] Checking password-reset endpoint")

    candidates = (
        "/reset_password",
        "/reset",
        "/forgot_password",
    )

    for path in candidates:
        url = urljoin(base, path)

        response = request(
            session,
            url,
            headers={"Host": canary},
        )

        if response is None:
            continue

        if response.status_code not in (404, 405):
            print(f"[+] Candidate reset endpoint: {path}")
            return path

    print("[-] No obvious reset endpoint")
    return None


def inspect_local_runtime():
    print("[*] Inspecting local container/runtime")

    import os
    import shutil
    import subprocess

    if shutil.which("runc"):
        try:
            output = subprocess.check_output(
                ["runc", "--version"],
                text=True,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            print(output.rstrip())
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"[-] runc inspection failed: {exc}")
    else:
        print("[-] runc is not available")

    if os.path.exists("/var/run/docker.sock"):
        print("[+] Docker socket exists")
        print("[!] This materially changes the attack surface")
    else:
        print("[-] Docker socket not present")


def main():
    parser = argparse.ArgumentParser(
        description="Web Challenge 2 reconnaissance/solver helper"
    )
    parser.add_argument(
        "target",
        help="URL of the booted challenge instance",
    )
    parser.add_argument(
        "--canary",
        default="webchallenge2-canary.invalid",
        help="Host-header canary value",
    )
    args = parser.parse_args()

    base = args.target.rstrip("/") + "/"

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Web-Challenge-2-Solver/1.0",
        }
    )

    print(f"[*] Target: {base}")

    fingerprint_ctfd(session, base)

    host_injection = test_host_header(
        session,
        base,
        args.canary,
    )

    if host_injection:
        test_reset_endpoint(
            session,
            base,
            args.canary,
        )

    inspect_local_runtime()

    print()
    if host_injection:
        print("[+] Most likely path: CTFd Host Header Injection")
        print("[+] Investigate CVE-2025-23001 / CTFd 3.7.5")
    else:
        print("[?] No confirmed web primitive yet")
        print("[?] If container access exists, inspect runc/Docker next")


if __name__ == "__main__":
    sys.exit(main())
