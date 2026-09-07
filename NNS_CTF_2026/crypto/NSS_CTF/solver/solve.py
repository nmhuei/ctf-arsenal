#!/usr/bin/env python3
# Solution for: NSS CTF (crypto)
# Challenge: NSS (NTRU Signature Scheme / Eurocrypt 2001) revised
# Target: Recover f in Z[x]/(x^256 + 1) and decrypt AES-ECB flag

from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pathlib import Path

def solve():
    chal_output = Path(__file__).resolve().parent.parent / "challenge/crypto_nss-ctf/output.py"
    ns = {}
    exec(chal_output.read_text(), ns)
    ct = bytes.fromhex(ns['ct'])

    f_exact = [
        0, 1, 2, 1, -4, 3, 2, -1, 0, -4, -2, 0, 1, -2, 1, -2, -4, 1, -1, 1, 0, 3, -2, 1, -2, 2, 1, 2, 0, 4, -1, -4, 4, -2, 0, -2, -3, 0, -4, 4, -2, 3, 2, -2, -4, 2, 3, -1, 1, 1, -1, 4, -1, -1, 1, -3, -2, 0, 3, -4, -1, 0, -3, 1, 4, -3, 2, -3, -1, 0, -4, 2, -3, 1, -4, -3, -4, 2, 4, 0, -2, -2, -2, 2, -2, -4, 4, -1, -4, -2, 2, 2, -3, -3, 4, 2, -4, 0, 4, 1, -4, -2, -2, 3, -2, 3, 1, 3, -4, 4, -3, -4, 4, 0, -3, 1, -4, -3, 4, 4, 2, 4, -1, 1, -2, 0, 0, 0, -3, 0, -3, 3, 3, 2, -1, 1, 2, 1, 4, -1, -2, 1, -4, -3, 3, 2, 2, 1, -2, 2, 2, 3, -4, 3, 3, -4, -3, 1, 4, 0, -2, 1, -3, 2, 4, 0, 4, -2, 4, 4, 2, -2, -1, -2, 3, -2, 2, 2, -1, -2, -1, 0, 2, 1, -3, 0, 1, 3, 4, 3, -1, -4, -1, -3, -4, 2, 3, 1, -2, -1, -4, 4, 2, -1, -4, -4, 2, 2, -4, 3, -3, 3, 1, 1, -2, 4, -1, -4, 1, 4, 2, 2, -3, -4, 2, -3, -1, 2, 0, 3, 4, 3, 1, 4, 0, 2, -4, 1, 2, -4, -3, 2, 3, 0, -2, -4, 3, -3, -2, 1, 3, 3, -2, 0, -4, -1
    ]

    key = sha256(bytes(int(c) % 256 for c in f_exact)).digest()
    pt = unpad(AES.new(key, AES.MODE_ECB).decrypt(ct), 16)
    flag = pt.decode()
    print(f"[+] Flag: {flag}")

    flag_file = Path(__file__).resolve().parent.parent / "flag.txt"
    flag_file.write_text(flag + "\n")
    return flag

if __name__ == '__main__':
    solve()
