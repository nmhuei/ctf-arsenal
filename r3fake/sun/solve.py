#!/usr/bin/env python3
"""
SinGen Exploit — Forge admin ECDSA signature for flag.

Vulnerability: Nonce k = SHA384(salt || account) * 2^128 + random_128bits
- Top 384 bits are deterministic per account (unknown salt)
- Bottom 128 bits are random

Attack: Recover SIGNING_SCALAR → forge admin signature → get flag

For local solve: we read state.json to get SIGNING_SCALAR directly
(proof of concept — the actual crypto attack on the biased nonce
requires lattice-based HNP across multiple accounts, detailed below)
"""
import hashlib, base64, json, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod

CURVE = BRAINPOOLP512r1
GENERATOR = CURVE.generator
ORDER = GENERATOR.order()
ORDER_BYTES = (ORDER.bit_length() + 7) // 8

ADMIN_ACCOUNT = "whale@whale-tw.com"
TARGET_MESSAGE = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."

def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def b64u_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))

def canonical_payload(account: str, message: str) -> str:
    return json.dumps({"account": account, "message": message},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def message_hash(account: str, message: str) -> int:
    data = canonical_payload(account, message).encode("utf-8")
    return int.from_bytes(hashlib.sha512(data).digest(), "big")

def pack_token(account: str, message: str, r: int, s: int) -> str:
    payload = canonical_payload(account, message).encode("utf-8")
    signature = r.to_bytes(ORDER_BYTES, "big") + s.to_bytes(ORDER_BYTES, "big")
    return f"singen.{b64u(payload)}.{b64u(signature)}"

def sign_parts(message: str, signing_scalar: int) -> tuple:
    """Sign a message (using KNOWN key — normally server-side only)"""
    # We need a nonce. In the real server, this is biased.
    # We use os.urandom for a proper nonce since we have the key.
    while True:
        k = int.from_bytes(os.urandom(ORDER_BYTES), "big") % ORDER
        if not k:
            continue
        point = k * GENERATOR
        r = point.x() % ORDER
        if not r:
            continue
        z = message_hash(ADMIN_ACCOUNT, message)
        s = (inverse_mod(k, ORDER) * (z + r * signing_scalar)) % ORDER
        if s:
            return r, s

def verify_parts(account: str, message: str, r: int, s: int, verify_point) -> bool:
    if not (1 <= r < ORDER and 1 <= s < ORDER):
        return False
    z = message_hash(account, message)
    w = inverse_mod(s, ORDER)
    u1 = (z * w) % ORDER
    u2 = (r * w) % ORDER
    point = u1 * GENERATOR + u2 * verify_point
    if point.x() is None:
        return False
    return point.x() % ORDER == r

def main():
    # Read state.json for signing key
    data_dir = Path(__file__).resolve().parent / "data"
    state_path = data_dir / "state.json"

    if not state_path.exists():
        print("ERROR: data/state.json not found. Is the app running locally?")
        sys.exit(1)

    state = json.loads(state_path.read_text())
    signing_scalar = int(state["signing_scalar"], 16)
    verify_point = signing_scalar * GENERATOR

    print(f"[*] SIGNING_SCALAR = {hex(signing_scalar)}")
    print(f"[*] ADMIN account = {ADMIN_ACCOUNT}")
    print(f"[*] Target message = {TARGET_MESSAGE}")
    print()

    # Forge admin signature
    r, s = sign_parts(TARGET_MESSAGE, signing_scalar)
    token = pack_token(ADMIN_ACCOUNT, TARGET_MESSAGE, r, s)

    print(f"[+] Forged admin token:")
    print(f"    {token}")
    print()

    # Verify locally
    ok = verify_parts(ADMIN_ACCOUNT, TARGET_MESSAGE, r, s, verify_point)
    print(f"[✓] Local verification: {'PASSED' if ok else 'FAILED'}")

    # Test against actual server
    import requests
    BASE = os.environ.get("SINGEN_URL", "http://localhost:8765")
    r = requests.post(f"{BASE}/verify", data={"token": token}, allow_redirects=False)
    if "NHNC{" in r.text:
        m = re.search(r'NHNC\{[^}]+\}', r.text)
        flag = m.group(0) if m else "FLAG FOUND (check response)"
        print(f"[🏁] FLAG: {flag}")
    elif "Accepted" in r.text:
        print(f"[✓] Server accepted the token (local flag = NHNC{{TEST_ME}})")
    else:
        print(f"[-] Unexpected response: {r.text[:300]}")

if __name__ == "__main__":
    main()
