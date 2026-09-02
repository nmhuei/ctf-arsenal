#!/usr/bin/env python3
import requests
import urllib3
import hashlib
import json
from ecdsa import SECP256k1, SigningKey

urllib3.disable_warnings()

TARGET = "https://370a0c93-475f-4c09-91da-532043e9afb4.222.255.138.122.nip.io"
CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def solve():
    # 1. Fetch public key
    r_pub = requests.get(f"{TARGET}/api/pubkey", verify=False)
    pub_data = r_pub.json()
    qx_target = pub_data["Qx"]
    print(f"[*] Target Public Key Qx: {qx_target}")

    # 2. Collect signatures until a nonce collision is found
    print("[*] Collecting signatures to find nonce reuse...")
    r_seen = {}
    m1, m2, r_val, s1, s2 = None, None, None, None, None

    for i in range(150):
        res = requests.get(f"{TARGET}/api/sign", verify=False).json()
        r_hex = res["r"]
        if r_hex in r_seen:
            sig1 = r_seen[r_hex]
            sig2 = res
            m1, m2 = sig1["message"], sig2["message"]
            r_val = int(r_hex, 16)
            s1 = int(sig1["s"], 16)
            s2 = int(sig2["s"], 16)
            print(f"[+] Nonce reuse found between 2 signatures!")
            break
        r_seen[r_hex] = res

    if not m1:
        print("[-] Could not find nonce reuse in sample size.")
        return None

    # 3. Recover Private Key d
    z1 = int.from_bytes(hashlib.sha256(m1.encode()).digest(), "big")
    z2 = int.from_bytes(hashlib.sha256(m2.encode()).digest(), "big")

    k = ((z1 - z2) * pow(s1 - s2, -1, CURVE_N)) % CURVE_N
    d = (pow(r_val, -1, CURVE_N) * (s1 * k - z1)) % CURVE_N

    sk = SigningKey.from_secret_exponent(d, curve=SECP256k1)
    vk = sk.get_verifying_key()
    qx_rec = hex(vk.pubkey.point.x())
    print(f"[+] Recovered Private Key: {hex(d)}")
    print(f"[*] Verified Qx: {qx_rec} (Matches: {qx_rec == qx_target})")

    # 4. Forge signature for 'give_flag' and redeem
    msg = b"give_flag"
    sig = sk.sign_deterministic(msg, hashfunc=hashlib.sha256)
    r_forged = int.from_bytes(sig[:32], "big")
    s_forged = int.from_bytes(sig[32:], "big")

    payload = {
        "message": "give_flag",
        "r": hex(r_forged),
        "s": hex(s_forged)
    }

    r_redeem = requests.post(f"{TARGET}/api/redeem", json=payload, verify=False)
    redeem_data = r_redeem.json()
    flag = redeem_data.get("flag")
    print(f"[+] Flag: {flag}")
    return flag

if __name__ == "__main__":
    solve()
