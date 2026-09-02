#!/usr/bin/env sage -python
"""
Exploit for authentification-2.

Run with Sage's Python:
    sage -python solve_authentification2_sage.py archive.cryptohack.org 61277
or:
    sage -python solve_authentification2_sage.py http://archive.cryptohack.org:61277
"""
import re
import sys
import json
import requests

try:
    from sage.all import GF, PolynomialRing
except Exception as exc:
    print("[-] This exploit needs SageMath for GF(2^128) polynomial roots.")
    print("    Run it as: sage -python solve_authentification2_sage.py <host> <port>")
    print(f"    Import error: {exc}")
    sys.exit(1)

BLOCK_LEN = 16
MASK128 = (1 << 128) - 1


def usage():
    print("usage:")
    print("  sage -python solve_authentification2_sage.py <URL>")
    print("  sage -python solve_authentification2_sage.py <HOST> <PORT>")
    sys.exit(1)


def normalize_url(argv):
    if len(argv) == 2:
        url = argv[1]
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        return url.rstrip("/")
    if len(argv) == 3:
        return f"http://{argv[1]}:{argv[2]}".rstrip("/")
    usage()


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def unquote_werkzeug_cookie(value):
    """Decode values like '"ct\\073tag"' into 'ct;tag'."""
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]

    def octal_repl(m):
        return chr(int(m.group(1), 8))

    value = re.sub(r"\\([0-7]{3})", octal_repl, value)
    value = value.replace(r"\073", ";")
    return value


def parse_token(cookie_value):
    cookie_value = unquote_werkzeug_cookie(cookie_value)
    if ";" not in cookie_value:
        raise ValueError(f"auth cookie has no separator after decoding: {cookie_value!r}")
    ct_hex, tag_hex = cookie_value.split(";", 1)
    return bytes.fromhex(ct_hex), bytes.fromhex(tag_hex)


def cookie_header_for_token(token):
    # Raw semicolons split Cookie header fields, so send Werkzeug's quoted/octal form.
    return 'auth="' + token.replace(";", r"\073") + '"'


# Same field representation as the challenge's GHASH:
# MSB of the 128-bit string is coefficient of x^0, so 0x80..00 is field 1.
F2 = GF(2)
R = PolynomialRing(F2, "z")
z = R.gen()
MOD = z**128 + z**7 + z**2 + z + 1
F = GF(2**128, name="a", modulus=MOD)
a = F.gen()
PR = PolynomialRing(F, "X")
X = PR.gen()


def bytes_to_field(b):
    if len(b) != BLOCK_LEN:
        raise ValueError("field elements must be 16 bytes")
    n = int.from_bytes(b, "big")
    out = F(0)
    # bit i, read MSB first, is coefficient of a^i
    for i in range(128):
        if (n >> (127 - i)) & 1:
            out += a**i
    return out


def field_to_bytes(e):
    poly = e.polynomial()
    n = 0
    for i, coeff in enumerate(poly.list()):
        if int(coeff) & 1:
            n |= 1 << (127 - i)
    return int(n & MASK128).to_bytes(16, "big")


def ghash_input_blocks(ciphertext):
    u = BLOCK_LEN * ((len(ciphertext) + BLOCK_LEN - 1) // BLOCK_LEN) - len(ciphertext)
    buf = ciphertext + (b"\x00" * u)
    # No AAD is used by the challenge, so len(A) = 0.
    buf += (0).to_bytes(8, "big")
    buf += (len(ciphertext) * 8).to_bytes(8, "big")
    return [buf[i:i + BLOCK_LEN] for i in range(0, len(buf), BLOCK_LEN)]


def ghash_poly_from_known_pair(ciphertext, tag, known_plaintext):
    # Because the broken implementation uses GCTR(J, P) and GCTR(J, S),
    # the first plaintext keystream block E_K(J) is also the tag mask.
    tag_mask = xor_bytes(ciphertext[:BLOCK_LEN], known_plaintext[:BLOCK_LEN])
    observed_s = xor_bytes(tag, tag_mask)

    blocks = [bytes_to_field(b) for b in ghash_input_blocks(ciphertext)]
    poly = bytes_to_field(observed_s)
    m = len(blocks)
    for i, block in enumerate(blocks):
        poly += block * (X ** (m - i))
    return poly, tag_mask


def ghash_eval(ciphertext, H):
    y = F(0)
    for block in ghash_input_blocks(ciphertext):
        y = (y + bytes_to_field(block)) * H
    return y


def extract_flag(html):
    # CryptoHack normally uses crypto{...}; the local default in the archive is BZHCTF{...}.
    m = re.search(r"(?:crypto|BZHCTF)\{[^}]+\}", html)
    if m:
        return m.group(0)
    m = re.search(r"[A-Za-z0-9_]+\{[^}]+\}", html)
    return m.group(0) if m else None


def main():
    url = normalize_url(sys.argv)
    s = requests.Session()

    username = "A" * 6
    password = "pw"
    known_plaintext = json.dumps({"username": username, "role": "guest"}).encode()
    target_plaintext = json.dumps({"username": "", "role": "super_admin"}).encode()
    assert len(known_plaintext) == len(target_plaintext) == 39

    print(f"[*] target: {url}")
    print("[*] resetting database/key and creating one chosen guest account")
    s.get(f"{url}/reset-db", timeout=10)
    s.cookies.clear()

    r = s.post(f"{url}/register", data={"username": username, "password": password}, allow_redirects=False, timeout=10)
    if r.status_code not in (200, 302, 303):
        print(f"[!] register returned HTTP {r.status_code}; continuing anyway")

    r = s.post(f"{url}/login", data={"username": username, "password": password}, allow_redirects=False, timeout=10)
    raw_auth = r.cookies.get("auth")
    if raw_auth is None:
        print("[-] login did not return an auth cookie")
        print(f"    HTTP {r.status_code}")
        print(r.text[:500])
        sys.exit(1)

    ciphertext, tag = parse_token(raw_auth)
    print(f"[*] captured token: {len(ciphertext)}-byte ciphertext, {len(tag)}-byte tag")

    if len(ciphertext) < len(target_plaintext):
        print("[-] chosen known plaintext is too short for target plaintext")
        sys.exit(1)

    keystream = xor_bytes(ciphertext, known_plaintext)
    forged_ciphertext = xor_bytes(target_plaintext, keystream[:len(target_plaintext)])

    poly, tag_mask = ghash_poly_from_known_pair(ciphertext, tag, known_plaintext)
    print(f"[*] solving degree-{poly.degree()} GHASH equation for H")
    roots = poly.roots(multiplicities=False)
    print(f"[*] candidate H values: {len(roots)}")
    if not roots:
        print("[-] no roots found; unexpected for a valid token")
        sys.exit(1)

    for idx, H in enumerate(roots, 1):
        forged_s = ghash_eval(forged_ciphertext, H)
        forged_tag = xor_bytes(field_to_bytes(forged_s), tag_mask)
        forged_token = forged_ciphertext.hex() + ";" + forged_tag.hex()
        headers = {"Cookie": cookie_header_for_token(forged_token)}
        rr = s.get(f"{url}/admin", headers=headers, timeout=10)
        flag = extract_flag(rr.text)
        if flag:
            print(f"[+] flag: {flag}")
            return
        print(f"[-] candidate {idx}/{len(roots)} rejected")

    print("[-] no candidate worked; response from last try:")
    print(rr.text[:1000])


if __name__ == "__main__":
    main()
