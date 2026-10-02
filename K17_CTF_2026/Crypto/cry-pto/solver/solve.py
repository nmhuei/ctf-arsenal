#!/usr/bin/env python3
"""Dynamic Solver for cry-pto (K17 CTF 2026 - Crypto).

Algebraic Vulnerability:
CRYSig evaluates signature bits via GF(2) linear inner products:
    res += (row & msg_vector).bit_count() % 2
Because this map is linear over GF(2), for any messages m1, m2:
    sign(m1 ^ m2) = sign(m1) ^ sign(m2)

Given:
    user = b"babyuser", target = b"chadr00t"
    sig(user) provided by server
We choose:
    query = user ^ target
Server returns:
    sig(query) = sig(user ^ target) = sig(user) ^ sig(target)
Therefore:
    sig(target) = sig(user) ^ sig(query)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
from pathlib import Path


def get_connection_info() -> tuple[str, int]:
    """Dynamically resolve host and port from environment, metadata.json, or README."""
    env_target = os.environ.get("TARGET_HOST")
    if env_target:
        if ":" in env_target:
            h, p = env_target.split(":", 1)
            return h.strip(), int(p.strip())
        return env_target.strip(), int(os.environ.get("TARGET_PORT", "2000"))

    meta_file = Path(__file__).resolve().parent.parent / "metadata.json"
    if meta_file.is_file():
        try:
            data = json.loads(meta_file.read_text())
            conn = data.get("connection_info")
            if conn and ":" in conn:
                h, p = conn.split(":", 1)
                return h.strip(), int(p.strip())
        except Exception:
            pass

    readme_file = Path(__file__).resolve().parent.parent / "challenge" / "README.md"
    if readme_file.is_file():
        text = readme_file.read_text()
        m = re.search(r"nc\s+([a-zA-Z0-9.-]+)\s+(\d+)", text)
        if m:
            return m.group(1), int(m.group(2))

    return "127.0.0.1", 2000


def get_target_users() -> tuple[bytes, bytes]:
    """Dynamically extract user and root usernames from chal.py if available."""
    chal_file = Path(__file__).resolve().parent.parent / "challenge" / "chal.py"
    user = b"babyuser"
    root = b"chadr00t"
    if chal_file.is_file():
        text = chal_file.read_text()
        m_user = re.search(r'user\s*=\s*b"([^"]+)"', text)
        m_root = re.search(r'root\s*=\s*b"([^"]+)"', text)
        if m_user:
            user = m_user.group(1).encode()
        if m_root:
            root = m_root.group(1).encode()
    return user, root


def recvuntil(sock: socket.socket, delim: bytes) -> bytes:
    buf = bytearray()
    while not buf.endswith(delim):
        chunk = sock.recv(1)
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)


def solve(host: str, port: int, user: bytes, root: bytes, timeout: float = 10.0) -> str:
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.create_connection((host, port), timeout=timeout)

    try:
        # Step 1: Read initial user signature
        line1 = recvuntil(s, b"\n").decode(errors="replace").strip()
        print(f"[*] Banner: {line1}")
        m_sig = re.search(r"signature:\s*([0-9a-fA-F]+)", line1)
        if not m_sig:
            raise ValueError(f"Could not parse user signature from banner: {line1}")
        user_sig = bytes.fromhex(m_sig.group(1))

        # Step 2: Query delta (user ^ root)
        delta_query = bytes([u ^ r for u, r in zip(user, root)])
        recvuntil(s, b"> ")
        s.sendall(delta_query.hex().encode() + b"\n")

        # Step 3: Read delta query signature
        line2 = recvuntil(s, b"\n").decode(errors="replace").strip()
        print(f"[*] Query response: {line2}")
        m_qsig = re.search(r"signature:\s*([0-9a-fA-F]+)", line2)
        if not m_qsig:
            raise ValueError(f"Could not parse query signature from response: {line2}")
        query_sig = bytes.fromhex(m_qsig.group(1))

        # Step 4: Compute root signature via linearity over GF(2)
        root_sig = bytes([u ^ q for u, q in zip(user_sig, query_sig)])
        print(f"[+] Computed target signature: {root_sig.hex()}")

        # Step 5: Send forged root signature and retrieve flag
        recvuntil(s, b"> ")
        s.sendall(root_sig.hex().encode() + b"\n")

        resp = s.recv(4096).decode(errors="replace")
        print(f"[*] Response: {resp.strip()}")

        m_flag = re.search(r"(?:K17|FLAG)\{[^}\r\n]+\}", resp)
        if not m_flag:
            raise RuntimeError(f"No flag pattern found in response: {resp}")

        flag = m_flag.group(0)
        print(f"[+] Recovered flag: {flag}")

        # Save flag locally
        flag_file = Path(__file__).resolve().parent.parent / "flag.txt"
        flag_file.write_text(flag + "\n")

        return flag
    finally:
        s.close()


def main():
    default_host, default_port = get_connection_info()
    default_user, default_root = get_target_users()

    parser = argparse.ArgumentParser(description="Solver for cry-pto")
    parser.add_argument("host", nargs="?", default=default_host, help=f"Host (default: {default_host})")
    parser.add_argument("port", nargs="?", type=int, default=default_port, help=f"Port (default: {default_port})")
    parser.add_argument("--user", default=default_user.decode(), help=f"Base username (default: {default_user.decode()})")
    parser.add_argument("--root", default=default_root.decode(), help=f"Target username (default: {default_root.decode()})")

    args = parser.parse_args()
    flag = solve(args.host, args.port, args.user.encode(), args.root.encode())
    print(f"\nFinal Flag: {flag}")


if __name__ == "__main__":
    main()
