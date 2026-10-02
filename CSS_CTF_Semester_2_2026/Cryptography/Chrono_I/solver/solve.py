#!/usr/bin/env python3
"""
Chrono I solver

Decrypts the ciphertext using the timestamp from the challenge message as a
numeric shift key.
"""

CIPHERTEXT = "ESUITO{gwfvb_xejqnf_nimgt_b_whhrlv}"
TIME_KEY = "20260921143507"


def decrypt(ciphertext: str, key: str) -> str:
    result = []
    key_index = 0

    for char in ciphertext:
        if char.isalpha():
            shift = int(key[key_index % len(key)])
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base - shift) % 26 + base))
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)


if __name__ == "__main__":
    flag = decrypt(CIPHERTEXT, TIME_KEY)
    print(flag)
