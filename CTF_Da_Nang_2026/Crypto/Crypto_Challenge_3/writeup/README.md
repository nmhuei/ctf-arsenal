# 🔐 Crypto Challenge 3: NovaSign (ECDSA Nonce Reuse)

- **Category:** Crypto
- **Points:** 600 pts
- **Status:** ✅ Solved
- **Flag:** `flag{ec0d141f-7b8b-4e1e-b4c7-ed4a154651c7}`

---

## 📖 Challenge Description

> *"Some Things Are Only Safe Because They Were Never Supposed to Happen Twice"*

The service **NovaSign** provides signed AI model responses via ECDSA on the `secp256k1` elliptic curve using SHA-256:
- `GET /api/pubkey`: Returns the service verifying key $(Q_x, Q_y)$.
- `GET /api/sign`: Returns a canonical JSON model message and its signature $(r, s)$.
- `POST /api/redeem`: Accepts `{"message": "give_flag", "r": "0x...", "s": "0x..."}` and rewards the flag if verified.

---

## 🔍 Vulnerability & Cryptanalysis

### 1. ECDSA Nonce Reuse Vulnerability
In standard ECDSA:
$$s \equiv k^{-1} (z + r \cdot d) \pmod n$$

Where:
- $n$ is the order of `secp256k1`: `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141`
- $z$ is the integer digest: $\text{SHA256}(m)$
- $d$ is the private key
- $k$ is the per-signature ephemeral nonce

When the same nonce $k$ is reused across two distinct messages $m_1$ and $m_2$, the signature $r$ value is identical for both:
$$s_1 - s_2 \equiv k^{-1} (z_1 - z_2) \pmod n$$

Solving for the nonce $k$:
$$k \equiv (z_1 - z_2) \cdot (s_1 - s_2)^{-1} \pmod n$$

Once $k$ is recovered, the private signing key $d$ is directly computed:
$$d \equiv r^{-1} (s_1 \cdot k - z_1) \pmod n$$

### 2. Attack Execution
1. Query `GET /api/sign` repeatedly (~60–70 requests) until two signatures share the same $r$ coordinate.
2. Extract $m_1, s_1$ and $m_2, s_2$, compute $z_1, z_2$, and calculate the private key $d$.
3. Verify that $d \cdot G = Q$.
4. Forge a valid ECDSA signature for the prohibited command message `"give_flag"`.
5. Submit the forged signature to `POST /api/redeem` to retrieve the flag.

---

## 🚀 Exploit Automation (`solve.py`)

```python
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
```

---

## 🎯 Verification Output
```bash
$ python3 solve.py
[*] Target Public Key Qx: 0x339340662663134abeea659793d53fabd8ad9fe56c5d206f98a81a2ff356f3c5
[*] Collecting signatures to find nonce reuse...
[+] Nonce reuse found between 2 signatures!
[+] Recovered Private Key: 0x9dd33bcd11bd9a64cb95712110337768f84583b4d7dfef72d5e1564de1c88340
[*] Verified Qx: 0x339340662663134abeea659793d53fabd8ad9fe56c5d206f98a81a2ff356f3c5 (Matches: True)
[+] Flag: flag{ec0d141f-7b8b-4e1e-b4c7-ed4a154651c7}
```
