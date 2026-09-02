#!/usr/bin/env sage
"""
SinGen Remote Exploit — SageMath LLL Attack

Attack: Given N ECDSA signatures from N different accounts where
  k_i = SHA384(salt || account_i) * 2^128 + T_i (T_i < 2^128)

Solve for d (signing key) by exploiting that:
- For each account, the low 128 bits of the nonce are "small"
- With enough accounts, LLL finds the unique key

Equation: a_i * d + b_i ≡ P_i * 2^128 + T_i (mod ORDER)
         where P_i < 2^384, T_i < 2^128
"""
import json, sys, os, hashlib, base64

ORDER = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

# Load signatures
try:
    import requests
    BASE = open("/tmp/instance_url.txt").read().strip()

    sigs = []
    for i in range(6):
        acct = f"k{i}@x.com"
        s = requests.Session()
        s.post(f"{BASE}/register", data={"email": acct, "password": "x"*8}, allow_redirects=False)
        s.post(f"{BASE}/login", data={"email": acct, "password": "x"*8}, allow_redirects=False)
        r = s.post(f"{BASE}/api/generate", json={"time":str(i),"motion":str((i+1)%50),"place":str((i+2)%50),"seat":str((i+3)%50)})
        if not r.ok: continue
        data = r.json()
        token = data.get("token","")
        if not token: continue
        parts = token.split(".")
        pl = json.loads(base64.urlsafe_b64decode(parts[1] + "==="))
        raw = base64.urlsafe_b64decode(parts[2] + "===")
        rv, sv = int.from_bytes(raw[:64],"big"), int.from_bytes(raw[64:],"big")
        cp = json.dumps({"account":pl["account"],"message":pl["message"]},ensure_ascii=False,sort_keys=True,separators=(",",":"))
        z = int.from_bytes(hashlib.sha512(cp.encode()).digest(),"big")
        a = int(pow(sv,-1,ORDER)*rv % ORDER)
        b = int(pow(sv,-1,ORDER)*z % ORDER)
        sigs.append({"a":a,"b":b,"r":rv,"s":sv,"z":z,"account":pl["account"]})
        print(f"[{i}] {acct}: collected")
except Exception as e:
    print(f"Error collecting: {e}")
    # try local file
    if os.path.exists("/tmp/sigs_remote.json"):
        sigs = json.load(open("/tmp/sigs_remote.json"))
    else:
        print("No sigs available")
        sys.exit(1)

N = len(sigs)
print(f"\n[*] {N} signatures collected")

# ── Lattice Construction ──
#
# For each equation: a_i * d + b_i ≡ k_i (mod ORDER)
#                   k_i = P_i * 2^128 + T_i, T_i < 2^128
#
# Let's set up:
#   A_i = a_i * 2^(-128) mod ORDER
#   B_i = b_i * 2^(-128) mod ORDER
# Then: A_i * d + B_i ≡ P_i + T_i * 2^(-128) (mod ORDER)
#
# P_i = SHA384(salt || account_i) is in [0, 2^384)
# So: (A_i * d + B_i) mod ORDER ≈ P_i (within T_i * inv_2_128 ≈ 2^128 * 2^384 ≈ 2^512 ≈ ORDER)
#
# This means: (A_i * d + B_i) mod ORDER < 2^384 (approximately)
# Actually it equals P_i + T_i * inv_2_128 mod ORDER.

# KEY INSTEAD: Use the fact that T_i is small in the ORIGINAL equation
# k_i = a_i * d + b_i (mod ORDER) → k_i is a number with T_i = k_i mod 2^128
#
# So: (a_i * d + b_i) mod ORDER ≡ T_i (mod 2^128)
# And T_i ∈ (0, 2^128)
#
# But T_i IS always a valid 128-bit value for ANY d.
# THE REAL CONSTRAINT IS ON THE HIGH BITS!
#
# k_i >> 128 = (a_i * d + b_i mod ORDER) >> 128 = P_i = SHA384(salt || account_i)
# This constrains ALL 512 bits of d.
#
# For 2 accounts: P_0 AND P_1 are both SHA384 outputs of the SAME salt
# This narrows d to ~2^512 * 2^(-384) * 2^(-384) = 2^512 * 2^(-768) ≈ 1 candidate

# But we CANNOT check if P_i is a SHA384 output without knowing the salt!

# ── PRACTICAL ATTACK ──
# What if we APPROXIMATE P_i by using the average?
# For a 384-bit SHA384 output: P_i ≈ 2^383 (expected value)
# For k_i = P_i*2^128 + T_i: k_i ≈ 2^383 * 2^128 = 2^511 ≈ ORDER/2
#
# So: a_i * d + b_i (mod ORDER) ≈ ORDER/2 (approximately)
# This gives a ROUGH estimate of d from EACH signature

# ── CVP LATTICE ──
# Form the CVP: find d such that k_i = a_i*d + b_i (mod ORDER)
# has the form k_i = P_i*2^128 + T_i
# The target lattice point is close to -b_i in each coordinate

from sage.all import *
F = GF(ORDER)
I = identity_matrix(ZZ, N)
A = vector(ZZ, [int(F(sigs[i]["a"]) * F(d)) for i in range(N) for d in ()])

# Actually let's build the proper lattice
# Standard approach: L = { (a_i * d + y_i * ORDER) for d ∈ Z, y_i ∈ Z }

L = matrix(ZZ, N + 1, N + 1)
for i in range(N):
    L[i,i] = ORDER
    L[i,N] = int(sigs[i]["a"]) % ORDER
L[N,N] = 1

# Target: T = (-b_0, -b_1, ..., -b_{N-1}, 0)
T = vector(ZZ, [int(-sigs[i]["b"]) % ORDER for i in range(N)] + [0])

print(f"\n[*] Lattice dimension: {N + 1}")
print(f"[*] Running LLL...")
L_lll = L.LLL()
print("[*] LLL done, checking short vectors...")

# Check each row of L_lll for potential d values
# A row of L_lll is a vector (y_i * ORDER + d * a_i) for some d, y_i
# The row + T should give (k_i) for some d

for row_idx, row in enumerate(L_lll):
    # row corresponds to (y_0 * ORDER + d*a_0, ..., d*a_{N-1} + y_{N-1}*ORDER, d)
    d_candidate = int(row[N])
    # Verify: does this d give k_i with T_i < 2^128?
    all_ok = True
    for i in range(N):
        k_i = int(F(sigs[i]["a"]) * F(d_candidate) + F(sigs[i]["b"]))
        T_i = k_i & ((1 << 128) - 1)
        if T_i >= (1 << 128):  # always false (it's a mod 2^128 value)
            all_ok = False
            break
    if all_ok:
        # Check if P_i = k_i >> 128 are consistent with SHA384
        # We can't check without salt, but we can check if P_i < 2^384 (always true)
        k = [int(F(sigs[i]["a"]) * F(d_candidate) + F(sigs[i]["b"])) for i in range(N)]
        P = [ki >> 128 for ki in k]
        if all(p < (1 << 384) for p in P):
            print(f"\n[!] Candidate d found in row {row_idx}!")
            print(f"    d = {hex(d_candidate)[:40]}...")

            # Check locally if this is the right key
            state_path = "/home/light/Workspace/CTF/r3fake/sun/data/state.json"
            if os.path.exists(state_path):
                state = json.load(open(state_path))
                local_d = int(state["signing_scalar"], 16)
                if d_candidate == local_d:
                    print("    MATCHES LOCAL KEY! This IS the remote key too!")
                    # Forge token
                    from ecdsa.curves import BRAINPOOLP512r1
                    G = BRAINPOOLP512r1.generator
                    admin = "whale@whale-tw.com"
                    target_msg = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
                    while True:
                        import os as _os
                        kk = int.from_bytes(_os.urandom(64), "big") % ORDER
                        if not kk: continue
                        pt = kk * G
                        rv = int(pt.x()) % ORDER
                        if not rv: continue
                        cp = json.dumps({"account":admin,"message":target_msg},ensure_ascii=False,sort_keys=True,separators=(",",":"))
                        zv = int.from_bytes(hashlib.sha512(cp.encode()).digest(),"big")
                        sv = int(pow(kk,-1,ORDER) * (zv + rv * d_candidate) % ORDER)
                        if sv: break
                    bb = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
                    token = f"singen.{bb(cp.encode())}.{bb(rv.to_bytes(64,'big')+sv.to_bytes(64,'big'))}"
                    print(f"\n[+] Forged token: {token[:80]}...")
                    try:
                        import requests
                        r = requests.post(f"{BASE}/verify", data={"token": token})
                        import re
                        m = re.search(r'NHNC\{[^}]+\}', r.text)
                        if m: print(f"\n[🏁] FLAG: {m.group(0)}")
                        else: print(f"Verify: {r.text[:300]}")
                    except: pass
                    break
else:
    print("\n[-] No valid d found in LLL output")
    print("[-] Trying BKZ with higher blocksize...")

    L_bkz = L.BKZ(block_size=min(N+1, 20))
    for row_idx, row in enumerate(L_bkz):
        d_candidate = int(row[N])
        if d_candidate == 0: continue
        k = [int(F(sigs[i]["a"]) * F(d_candidate) + F(sigs[i]["b"])) for i in range(N)]
        # Check if k values have the structure we expect
        # Extract T_i and check they're reasonable
        for i in range(N):
            T_i = k[i] & ((1 << 128) - 1)

        # Verify consistency: P_i should pass the SHA384 salt test
        # We can't test this without salt, but at minimum they should be < 2^384
        P = [ki >> 128 for ki in k]
        if all(p < (1 << 384) and p > 0 for p in P):
            print(f"[!] BKZ found: d={hex(d_candidate)[:30]}...")
            break

print("\n[*] DONE")
