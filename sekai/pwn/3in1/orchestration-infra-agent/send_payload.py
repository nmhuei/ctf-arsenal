#!/usr/bin/env python3
"""
send_payload.py — Orchestration infra agent payload sender.

Protocol (run.py):
  1. Opens TCP port, reads one line of base64 from stdin
  2. Decodes base64, appends "//" (JS comment guard)
  3. Writes to tempfile, executes run.sh → QEMU with Ladybird JS
  4. stdout from QEMU process is returned over the TCP connection

Result classification:
  - clean_exit       : process returned 0, no error signals
  - kernel_panic     : output contains "Kernel panic" or "BUG:"
  - qemu_crash       : connection dropped without clean exit
  - timeout          : did not complete within TIMEOUT seconds
  - flag             : output contains SEKA I{...} flag pattern
  - error            : other non-zero return
"""

import argparse
import base64
import hashlib
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 180
DEFAULT_LOG = "work/shared/run_log.jsonl"

FLAG_PATTERNS = [
    b"SEKAI{",
    b"flag{",
    b"FLAG{",
    b"sekai{",
]

PANIC_PATTERNS = [
    b"Kernel panic",
    b"BUG:",
    b"Unable to handle kernel",
    b"general protection fault",
    b"kernel BUG",
    b"Oops:",
]

QEMU_CRASH_PATTERNS = [
    b"qemu: fatal",
    b"abort",
    b"Segmentation fault",
]


def classify_result(stdout: bytes, returncode: int) -> str:
    """Classify QEMU run result into a short string tag."""
    # Flag match takes highest priority
    for pat in FLAG_PATTERNS:
        if pat in stdout:
            return "flag"

    # Kernel panic
    for pat in PANIC_PATTERNS:
        if pat in stdout:
            return "kernel_panic"

    # QEMU crash
    for pat in QEMU_CRASH_PATTERNS:
        if pat in stdout:
            return "qemu_crash"

    if returncode == 0:
        return "clean_exit"
    if returncode == 124:  # timeout from run.py
        return "timeout"
    if returncode == -11:
        return "segfault"
    return "error"


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def recv_all(sock: socket.socket, timeout: float) -> bytes:
    """Read until the socket is closed or timeout."""
    sock.settimeout(timeout)
    chunks = []
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    except socket.timeout:
        pass
    except ConnectionResetError:
        pass
    except BrokenPipeError:
        pass
    return b"".join(chunks)


def run_iteration(
    payload: bytes,
    host: str,
    port: int,
    timeout: float,
) -> dict:
    """
    Connect to host:port, send base64-encoded payload, read response.

    Returns dict with timestamp, payload_hash, result_class, stdout_tail,
    returncode.
    """
    ts = datetime.now(timezone.utc).isoformat()
    payload_b64 = base64.b64encode(payload).decode()
    start = time.monotonic()

    result_class = "unknown"
    returncode = -1
    stdout = b""
    error_msg = None

    try:
        sock = socket.create_connection((host, port), timeout=10)
    except (ConnectionRefusedError, OSError) as e:
        return {
            "timestamp": ts,
            "payload_hash": compute_hash(payload),
            "result_class": "connection_refused",
            "stdout_tail": str(e),
            "returncode": -1,
            "elapsed": time.monotonic() - start,
        }

    try:
        # Read prompt
        prompt = recv_all(sock, timeout=5)
        if not prompt:
            sock.close()
            return {
                "timestamp": ts,
                "payload_hash": compute_hash(payload),
                "result_class": "no_prompt",
                "stdout_tail": "",
                "returncode": -1,
                "elapsed": time.monotonic() - start,
            }

        # Send payload
        sock.sendall((payload_b64 + "\n").encode())

        # Read response until socket closes
        stdout = recv_all(sock, timeout=timeout)
        returncode = 0

    except socket.timeout:
        result_class = "timeout"
        returncode = 124
    except ConnectionResetError:
        result_class = "qemu_crash"
        returncode = -1
    except BrokenPipeError:
        result_class = "qemu_crash"
        returncode = -1
    except Exception as e:
        error_msg = str(e)
        result_class = "error"
        returncode = -1
    finally:
        try:
            sock.close()
        except Exception:
            pass

    if not error_msg and result_class == "unknown":
        result_class = classify_result(stdout, returncode)

    elapsed = time.monotonic() - start
    # Truncate stdout tail to 500 chars for logging
    stdout_text = stdout.decode("utf-8", errors="replace")
    stdout_tail = stdout_text[-500:] if len(stdout_text) > 500 else stdout_text
    if error_msg:
        stdout_tail = f"{stdout_tail} | ERROR: {error_msg}"

    return {
        "timestamp": ts,
        "payload_hash": compute_hash(payload),
        "result_class": result_class,
        "stdout_tail": stdout_tail,
        "returncode": returncode,
        "elapsed": elapsed,
    }


def load_payload(payload_file: str | None, base64_str: str | None) -> bytes:
    """Load payload from file path or base64 string."""
    if payload_file:
        if payload_file == "-":
            return sys.stdin.buffer.read()
        path = Path(payload_file)
        if not path.exists():
            print(f"error: payload file not found: {payload_file}", file=sys.stderr)
            sys.exit(1)
        return path.read_bytes()
    if base64_str:
        return base64.b64decode(base64_str)
    print("error: either --file or --base64 is required", file=sys.stderr)
    sys.exit(1)


def append_log(log_path: str, record: dict) -> None:
    """Append one JSONL record to log file, creating parent dirs if needed."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def summary(results: list[dict]) -> None:
    """Print summary table to stderr."""
    total = len(results)
    classes = {}
    for r in results:
        cls = r["result_class"]
        classes[cls] = classes.get(cls, 0) + 1
    print(f"--- Summary: {total} iteration(s) ---", file=sys.stderr)
    for cls, cnt in sorted(classes.items(), key=lambda x: -x[1]):
        print(f"  {cls}: {cnt}", file=sys.stderr)
    print(file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Send exploit payload to pwn_3in1 QEMU runner."
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("-f", "--file", help="Payload file path (use '-' for stdin)")
    src.add_argument("--base64", help="Base64-encoded payload string")

    ap.add_argument("--host", default=DEFAULT_HOST, help=f"Target host (default: {DEFAULT_HOST})")
    ap.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, help=f"Target port (default: {DEFAULT_PORT})")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Timeout per iteration (default: {DEFAULT_TIMEOUT}s)")
    ap.add_argument("-n", "--iterations", type=int, default=1, help="Number of iterations (default: 1)")
    ap.add_argument("--log", default=DEFAULT_LOG, help=f"JSONL log path (default: {DEFAULT_LOG})")
    ap.add_argument("-v", "--verbose", action="store_true", help="Print full stdout to stderr")

    args = ap.parse_args()

    payload = load_payload(args.file, args.base64)
    print(f"[*] Payload: {len(payload)} bytes, hash={compute_hash(payload)}", file=sys.stderr)

    results = []
    for i in range(args.iterations):
        label = f"[{i+1}/{args.iterations}]" if args.iterations > 1 else ""
        print(f"{label} Sending to {args.host}:{args.port} ...", file=sys.stderr)

        result = run_iteration(payload, args.host, args.port, args.timeout)
        results.append(result)
        append_log(args.log, result)

        print(f"  -> result_class={result['result_class']} returncode={result['returncode']} elapsed={result['elapsed']:.1f}s", file=sys.stderr)
        if args.verbose and result["stdout_tail"]:
            print(f"  --- stdout tail ---\n{result['stdout_tail']}\n  ---", file=sys.stderr)

        if i + 1 < args.iterations:
            time.sleep(1)

    summary(results)

    # Print the last result as machine-readable JSON to stdout
    if results:
        print(json.dumps(results[-1], ensure_ascii=False))


if __name__ == "__main__":
    main()
