#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import secrets
import subprocess
import sys
from math import gcd
from pathlib import Path

from Crypto.Util.number import bytes_to_long, getPrime


E = 65537
PRIME_BITS = 140
PASSWORD_MODE = 'random_password'
CHUNK_COUNT = 1


def password_material() -> bytes:
    if PASSWORD_MODE == "sha256_digest":
        flag = os.environ.get("GZCTF_FLAG") or os.environ.get("FLAG") or "PTITCTF{local_test_flag}"
        return hashlib.sha256(flag.encode("utf-8")).hexdigest().encode("ascii")
    if PASSWORD_MODE == "random_password":
        return secrets.token_hex(16).encode("ascii")
    raise ValueError(f"unknown password mode: {PASSWORD_MODE}")


def split_password(password: bytes) -> list[bytes]:
    if CHUNK_COUNT == 1:
        return [password]
    if len(password) % CHUNK_COUNT != 0:
        raise ValueError("password length is not divisible by CHUNK_COUNT")
    size = len(password) // CHUNK_COUNT
    return [password[index:index + size] for index in range(0, len(password), size)]


def generate_rsa_segment(plaintext: bytes) -> dict[str, int]:
    while True:
        p = getPrime(PRIME_BITS)
        q = getPrime(PRIME_BITS)
        phi = (p - 1) * (q - 1)
        if p != q and gcd(E, phi) == 1:
            break
    n = p * q
    m = bytes_to_long(plaintext)
    if m >= n:
        raise ValueError("password chunk is too large for RSA modulus")
    return {"n": n, "e": E, "c": pow(m, E, n)}


def create_zip(input_dir: Path, output_zip: Path, password: bytes) -> None:
    script = Path(__file__).resolve().with_name("zip_with_sha256_password.py")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "-i",
            str(input_dir),
            "-o",
            str(output_zip),
            "--password",
            password.decode("ascii"),
        ],
        check=True,
    )


def generate(input_dir: Path, output_zip: Path) -> list[dict[str, int]]:
    password = password_material()
    segments = [generate_rsa_segment(chunk) for chunk in split_password(password)]
    create_zip(input_dir, output_zip, password)
    return segments


# PUBLIC_SEGMENTS = [{'n': 896949230945185690784357873607286096026939890506455813174654286411035237740830823033, 'e': 65537, 'c': 657641959431153475104152317673005267940954209281742690106700466759779820469761753118}]
