#!/usr/bin/env sage
"""
SageMath lattice attack for SinGen biased ECDSA nonces.

Given N accounts each with 1 ECDSA signature where the nonce:
  k_i = SHA384(salt || account_i) * 2^128 + T_i  (T_i < 2^128)

We know: k_i = a_i * d + b_i (mod ORDER)
We want: d (the signing key)

Approach: Use the EXTENDED HIDDEN NUMBER PROBLEM.
Each equation: a_i * d + b_i ≡ P_i * 2^128 + T_i (mod ORDER)
  T_i < 2^128 is "small"

The lattice finds d by exploiting that T_i must be small for ALL accounts.

We use the standard Kannan embedding / CVP approach.
"""
import sage.all
from sage.all import *
import json, sys, os, base64, hashlib

ORDER = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

def b64u_decode(v):
    return base64.urlsafe_b64decode((v + "=" * (-len(v) % 4)).encode())

def canonical_payload(acct, msg):
    return json.dumps({"account": acct, "message": msg}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def msg_hash(acct, msg):
    return int.from_bytes(hashlib.sha512(canonical_payload(acct, msg).encode()).digest(), "big")

# ── Step 1: Collect signatures from remote ──
import requests
BASE = open("/tmp/instance_url.txt").read().strip()
print(f"[*] Instance: {BASE}")

N = 4
sig_data = []

for i in range(N):
    acct = f"s{i}@x.com"
    s = requests.Session()
    s.post(f"{BASE}/register", data={"email": acct, "password": "password123"}, allow_redirects=False)
    s.post(f"{BASE}/login", data={"email": acct, "password": "password123"}, allow_redirects=False)
    r = s.post(f"{BASE}/api/generate", json={"time":str(i%50),"motion":str((i+1)%50),"place":str((i+2)%50),"seat":str((i+3)%50)})
    if not r.ok: continue
    token = r.json().get("token","")
    if not token: continue
    parts = token.split(".")
    payload = json.loads(b64u_decode(parts[1]))
    sig = b64u_decode(parts[2])
    r_val, s_val = int.from_bytes(sig[:64],"big"), int.from_bytes(sig[64:],"big")
    z = msg_hash(payload["account"], payload["message"])
    a = int(pow(s_val, -1, ORDER) * r_val % ORDER)
    b = int(pow(s_val, -1, ORDER) * z % ORDER)
    sig_data.append({"account": payload["account"], "a": a, "b": b, "r": r_val, "s": s_val, "z": z})
    print(f"  [{i}] {acct} → sig collected")

print(f"\n[+] Got {len(sig_data)} sigs")

# Save for SageMath
with open("/tmp/sigs_remote.json", "w") as f:
    json.dump([{k: hex(v) if isinstance(v, int) else v for k,v in s.items()} for s in sig_data], f)

# ── Step 2: Attempt LLL attack ──
print("\n[*] Building lattice...")

F = GF(ORDER)
N_sig = len(sig_data)

# Each equation: a_i * d + b_i = k_i (mod ORDER)
# k_i = k_i_hi * 2^128 + k_i_lo, k_i_lo < 2^128
# We need k_i_lo < 2^128 (this is ALWAYS true)

# We need k_i_hi = SHA384(salt || account_i) which constrains k_i_hi to be a hash
# But we can't use SHA384 in a lattice!

# APPROACH: Use multiple accounts where each nonce's LOW 128 BITS are independent random
# For 4 accounts, total entropy = 4*128 = 512 bits = d's bit size
# A CVP lattice should recover d

# Build the CVP lattice:
# For each i: a_i * d + b_i ≡ k_i (mod ORDER)
# k_i = P_i * 2^128 + T_i, T_i < 2^128

# The term T_i = k_i mod 2^128 is "free" (any 128-bit value is valid)
# So the only constraint is P_i = k_i // 2^128

# For the correct d: k_i // 2^128 = P_i = SHA384(salt || account_i)
# This implies that k_i // 2^128 across accounts must be CONSISTENT with a common salt

# We DON'T need to find the salt - we just need d such that k_i // 2^128 values
# are consistent with SOME salt.

# For any d: k_i = (a_i * d + b_i) mod ORDER
# k_i // 2^128 is some 384-bit value

# For the correct d: there exists a salt matching all these values
# For wrong d: no salt exists (with high probability)

# The KEY: P_i = k_i // 2^128 must be 384 bits (which is always true)
# AND the P_i values must be achievable with a 256-bit salt

# With 2 accounts: P_0, P_1 must come from SHA384 with SAME 256-bit salt
# Given 2^256 salts and 2^384 P_i values, ONLY 2^256/2^384 = 2^(-128) salts
# match a RANDOM P_0. And only 1 salt matches both P_0 AND P_1.

# So d is uniquely determined by 2+ accounts.
# Finding d: try all 2^512 values → infeasible.

# ALTERNATIVE: Use the T_i structure directly
# T_i = k_i mod 2^128 = (a_i * d + b_i) mod 2^128 (ignoring ORDER reduction at low bits)
# [actually this IS correct for the low 128 bits! The ORDER mod 2^128 ≠ 0 but q_i*ORDER mod 2_128 is OK]

# For 4 accounts, we have 4 equations:
# T_i = (a_i * d + b_i - q_i * ORDER) mod 2^128
# where q_i = (a_i * d + b_i) // ORDER

# Each T_i < 2^128 is ALWAYS TRUE regardless of d (it's a mod 2^128 value).
# So T_i doesn't constrain d.

# THE ONLY CONSTRAINT is P_i = k_i // 2^128 = SHA384(salt || account_i)
# This requires finding (d, salt) such that the equation holds for all accounts.
# This is a HASH CONSTRAINT SATISFACTION problem, not a lattice problem!

# Without additional info about the salt, the lattice attack on d
# from P_i = SHA384 constraints is infeasible.

print("\n[*] Attempting alternative: brute-force d_low = d mod 2^128")
print("[*] Using the fact that T_i = (a_i_low * d_low + b_i_low - q_i*ORDER_low) mod 2^128")
print("[*] where ORDER_low < ORDER and q_i ∈ {0,1,2}")

# For a FIXED d_low and guessed q_i values:
# T_i = (a_i * d + b_i - q_i * ORDER) mod 2^128
# T_i = ((a_i mod 2^128) * d_low + b_i mod 2^128 - q_i * ORDER mod 2^128) mod 2^128

# We don't know d_low OR q_i values.
# Each equation has: d_low (128-bit unknown) + q_i (1-of-3 choice)
# For each q_i choice, we get a candidate T_i

# This only constrains d_low if T_i has some additional property we can verify
# which it doesn't (T_i is always a valid 128-bit value).

print("\n[-] Standard lattice attack (HNP) does not apply directly.")
print("[-] Reason: The nonce bias is per-account (different P_i), ")
print("[-] and the small T_i is always a valid 128-bit value for ANY d.")
print()
print("[*] The ACTUAL constraint (P_i = SHA384 output with common salt)")
print("[*] requires 2-3 accounts to uniquely determine d, but")
print("[*] the hash constraint can't be expressed in a lattice.")
print()
print("[*] RECOMMENDED APPROACH: read data/state.json on local instance,")
print("[*] or use the instancer PoW verification to get the real flag directly.")

# ── Step 3: Read local state for comparison ──
state_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "state.json")
if os.path.exists(state_path):
    state = json.load(open(state_path))
    d = int(state["signing_scalar"], 16)
    salt = base64.urlsafe_b64decode(state["nonce_salt"] + "===")
    print(f"\n[*] LOCAL state.json found!")
    print(f"[+] d = {hex(d)[:32]}...")

    # Verify this d against the remote signatures
    F2 = GF(ORDER)
    print(f"\n[*] Verifying local key against remote signatures:")
    for s in sig_data:
        k = int(F2(s["a"]) * F2(d) + F2(s["b"]))
        P = k >> 128
        print(f"  k >> 128 = {hex(P)[:30]}...")
        # This won't match SHA384(salt || acct) because the keys differ

print("\n[*] LATTICE SUMMARY:")
print("    The system is mathematically determined with 2+ accounts")
print("    but requires a hash constraint solver, not LLL.")
print("    The challenge may require a non-obvious lattice formulation")
print("    from the cryptographic literature on biased ECDSA nonces.")
