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
PASSWORD_MODE = 'sha256_digest'
CHUNK_COUNT = 4


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


# PUBLIC_SEGMENTS = [{'n': 873873167216667415925389352820510988646315303227397431498081714589380007929190731589, 'e': 65537, 'c': 652706433124336101372746217341650114286828436577474864839324654621680294265053201780}, {'n': 727797926731636564868904933554532277343734508845547196491720662294948980830717076317, 'e': 65537, 'c': 238693122670312949487812687737554989739417466938418119400287697506051689931529093073}, {'n': 721204840774291488465326329714992405354109786372760210571280840284842978179288645769, 'e': 65537, 'c': 359141758878318547421311451735591046114624726235138017111364988525645680918201621510}, {'n': 1505162753392977848428844959817177420559919681351822962793927830044548837293859649963, 'e': 65537, 'c': 1464723384740420932930400683019676271506349458484667145330284881917958324423034110743}]
