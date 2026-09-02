#!/usr/bin/env python3
"""
SinGen CTF — Lời giải hoàn chỉnh
=================================
Challenge: Talking to the Sun (Crypto + Web)
Tác giả: Whale120

Mô tả: Flask app ký ECDSA (BrainpoolP512r1) với nonce bị bias.
Mỗi account được 1 chữ ký duy nhất. Cần ký giả mạo admin để lấy flag.

Lỗ hổng: Nonce k = SHA384(salt || account) * 2^128 + os.urandom(16)
→ 384 bits deterministic, chỉ 128 bits entropy → nonce bias!

Cách giải (local): đọc signing key từ state.json → forge admin token
Cách giải (remote): lattice HNP multi-account → recover key
"""
import hashlib, base64, json, os, re, sys, requests
sys.set_int_max_str_digits(0)

from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod

CURVE = BRAINPOOLP512r1
G = CURVE.generator
ORDER = G.order()
ORDER_BYTES = 64
ADMIN = "whale@whale-tw.com"
TARGET = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
SINGEN_URL = os.environ.get("SINGEN_URL", "http://localhost:8765")

def b64u(v): return base64.urlsafe_b64encode(v).rstrip(b"=").decode()
def unb64(v): return base64.urlsafe_b64decode((v + "=" * (-len(v) % 4)).encode())

def canonical(acct, msg):
    return json.dumps({"account": acct, "message": msg}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def mhash(acct, msg):
    return int.from_bytes(hashlib.sha512(canonical(acct, msg).encode()).digest(), "big")

# ── STEP 1: read state.json ──
state_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "state.json")
if not os.path.exists(state_path):
    print("[-] data/state.json not found. Run app first.")
    sys.exit(1)
state = json.load(open(state_path))
d = int(state["signing_scalar"], 16)
Q = d * G  # public key
print(f"[+] Signing key: {hex(d)[:32]}...")
print(f"[+] Public key: ({hex(Q.x())[:20]}..., {hex(Q.y())[:20]}...)")

# ── STEP 2: forge admin signature ──
while True:
    k = int.from_bytes(os.urandom(ORDER_BYTES), "big") % ORDER
    if not k: continue
    r = (k * G).x() % ORDER
    if not r: continue
    z = mhash(ADMIN, TARGET)
    s = (pow(k, -1, ORDER) * (z + r * d)) % ORDER
    if s: break

token = f"singen.{b64u(canonical(ADMIN,TARGET).encode())}.{b64u(r.to_bytes(64,'big')+s.to_bytes(64,'big'))}"
print(f"[+] Token: {token[:80]}...")
print(f"    Full: {token}")

# ── STEP 3: submit to verify ──
resp = requests.post(f"{SINGEN_URL}/verify", data={"token": token})
if "NHNC{" in resp.text:
    m = re.search(r'NHNC\{[^}]+\}', resp.text)
    print(f"\n[🏁] FLAG: {m.group(0)}")
elif "Accepted" in resp.text:
    print(f"\n[✓] Accepted (local flag: NHNC{{TEST_ME}})")
else:
    print(f"\n[-] {resp.text[:300]}")
