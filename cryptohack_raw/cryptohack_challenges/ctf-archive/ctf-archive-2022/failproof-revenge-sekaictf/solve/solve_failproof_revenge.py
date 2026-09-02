#!/usr/bin/env python3
"""
Exploit for FaILProof Revenge (SekaiCTF / CryptoHack archive).

Local:
    python3 solve_failproof_revenge.py local /path/to/source.py
Remote:
    python3 solve_failproof_revenge.py remote archive.cryptohack.org 36813

Dependency: scipy >= 1.9 with scipy.optimize.milp.
"""
import ast
import hashlib
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def gen_pubkey(secret: bytes) -> list[int]:
    h = lambda m: hashlib.sha512(m).digest()
    state = h(secret)
    pubkey = []
    for _ in range(len(h(b"0")) * 4):
        pubkey.append(int.from_bytes(state, "big"))
        state = h(state)
    return pubkey


def build_matrix(pubkey: list[int]) -> np.ndarray:
    # x[0] is the MSB of the 64-byte block, x[511] the LSB.
    return np.array([[(a >> (511 - k)) & 1 for k in range(512)] for a in pubkey], dtype=np.float64)


def parse_output(data: str):
    lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
    if len(lines) < 2:
        raise ValueError("expected two lines from challenge: secret hex and ciphertext list")
    return lines[0], ast.literal_eval("\n".join(lines[1:]))


def byte_fix_rows(byte_offset: int, value: int):
    """Return rows fixing one plaintext byte inside the hidden 8-byte message segment."""
    rows, vals = [], []
    bit_base = 24 * 8 + byte_offset * 8
    for k in range(8):
        row = np.zeros(512, dtype=np.float64)
        row[bit_base + k] = 1
        rows.append(row)
        vals.append((value >> (7 - k)) & 1)
    return rows, vals


def solve_one_block(A: np.ndarray, counts: list[int], block_index: int, known_prefix: bytes = b"", time_limit: int = 120) -> bytes:
    b = np.array(counts, dtype=np.float64)
    C_rows = [*A]
    lb = list(b)
    ub = list(b)

    # The original event flag starts with SEKAI{. Fixing those known bytes makes block 0 much easier.
    if block_index == 0 and known_prefix:
        for pos, ch in enumerate(known_prefix[:8]):
            rows, vals = byte_fix_rows(pos, ch)
            C_rows.extend(rows)
            lb.extend(vals)
            ub.extend(vals)

    C = np.vstack(C_rows)
    constraints = LinearConstraint(C, np.array(lb, dtype=np.float64), np.array(ub, dtype=np.float64))

    # Try a few objectives. The system is usually uniquely feasible, but different objectives help HiGHS.
    objectives = [np.zeros(512, dtype=np.float64), np.ones(512, dtype=np.float64), -np.ones(512, dtype=np.float64)]
    rng = np.random.default_rng(0xC0FFEE + block_index)
    objectives += [rng.standard_normal(512) for _ in range(3)]

    last_status = None
    last_message = ""
    for obj_id, obj in enumerate(objectives):
        t0 = time.time()
        res = milp(
            c=obj,
            integrality=np.ones(512, dtype=np.int8),
            bounds=Bounds(0, 1),
            constraints=constraints,
            options={"time_limit": time_limit, "mip_rel_gap": 0, "presolve": True},
        )
        last_status, last_message = res.status, res.message
        if res.x is None or res.status != 0:
            print(f"[!] block {block_index:02d}, objective {obj_id}: {res.message} ({time.time() - t0:.2f}s)", flush=True)
            continue

        x = np.rint(res.x).astype(np.uint8)
        # Validate with exact small integers.
        if not np.array_equal(A.astype(np.int16) @ x.astype(np.int16), b.astype(np.int16)):
            print(f"[!] block {block_index:02d}, objective {obj_id}: invalid rounded solution", flush=True)
            continue

        full_block = int("".join(map(str, x.tolist())), 2).to_bytes(64, "big")
        msg = full_block[24:32]
        print(f"[+] block {block_index:02d}: {msg!r} ({time.time() - t0:.2f}s)", flush=True)
        return msg

    raise RuntimeError(f"failed on block {block_index}: status={last_status}, message={last_message}")


def solve(secret_hex: str, enc: list[list[int]], known_prefix: bytes = b"SEKAI{") -> bytes:
    secret = bytes.fromhex(secret_hex)
    A = build_matrix(gen_pubkey(secret))
    out = bytearray()
    for i, counts in enumerate(enc):
        out += solve_one_block(A, counts, i, known_prefix=known_prefix)
    return bytes(out).rstrip(b"\x00")


def find_source(argv_path: str | None) -> str:
    if argv_path:
        return argv_path
    here = Path.cwd()
    hits = list(here.rglob("source_*.py")) + list(here.rglob("source.py"))
    if not hits:
        raise FileNotFoundError("pass the path to source.py, e.g. python3 solve_failproof_revenge.py local files/source_xxx.py")
    return str(hits[0])


def run_local(source_path: str | None):
    source = find_source(source_path)
    test_flag = b"SEKAI{abc}"
    env = os.environ.copy()
    env["FLAG"] = test_flag.decode()
    data = subprocess.check_output([sys.executable, source], env=env, text=True)
    secret_hex, enc = parse_output(data)
    flag = solve(secret_hex, enc)
    print(f"[+] local recovered: {flag!r}")
    if flag != test_flag:
        raise SystemExit(f"local test failed: expected {test_flag!r}, got {flag!r}")
    print("[+] local OK")


def recv_remote(host: str, port: int, timeout: int = 20) -> str:
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        chunks = []
        while True:
            try:
                chunk = s.recv(65536)
            except socket.timeout:
                break
            if not chunk:
                break
            chunks.append(chunk)
    return b"".join(chunks).decode(errors="replace")


def run_remote(host: str, port: int):
    data = recv_remote(host, port)
    print(f"[+] received {len(data)} chars")
    secret_hex, enc = parse_output(data)
    print(f"[+] secret = {secret_hex}")
    print(f"[+] blocks = {len(enc)}")
    flag = solve(secret_hex, enc)
    print(f"[+] FLAG: {flag.decode(errors='replace')}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    if mode == "local":
        run_local(sys.argv[2] if len(sys.argv) > 2 else None)
    elif mode == "remote":
        host = sys.argv[2] if len(sys.argv) > 2 else "archive.cryptohack.org"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 36813
        run_remote(host, port)
    else:
        print("Usage:")
        print("  python3 solve_failproof_revenge.py local /path/to/source.py")
        print("  python3 solve_failproof_revenge.py remote archive.cryptohack.org 36813")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
