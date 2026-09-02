#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIA - What does 'I' stand for? (PTIT CTF 2026 - Crypto)
Single-file Automated Solver (Sequential 12-thread SIQS with -noecm)
"""
import os
import sys
import re
import json
import socket
import urllib.request
import subprocess
import ast
from Crypto.Util.number import long_to_bytes

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
YAFU_DIR = os.path.join(WORKSPACE_DIR, "script/yafu_src")
TEMP_DIR = os.path.join(WORKSPACE_DIR, "temp_run")

def lookup_factordb(n: int) -> tuple[int, int] | None:
    """Fast check on FactorDB API."""
    try:
        url = f"http://factordb.com/api?query={n}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") in ["FF", "CF"]:
                factors = [int(f[0]) for f in data.get("factors", []) if int(f[0]) > 1]
                if len(factors) >= 2 and factors[0] * factors[1] == n:
                    print(f"[+] FactorDB instant hit for n = {n}!")
                    return factors[0], factors[1]
    except Exception:
        pass
    return None

def factor_n(n: int, threads: int = 12) -> tuple[int, int]:
    """Factors a 280-bit RSA modulus using FactorDB or YAFU SIQS (-noecm)."""
    # 1. Try FactorDB first (instant ~0.1s)
    cached = lookup_factordb(n)
    if cached:
        return cached

    # 2. Run YAFU SIQS with full 12 threads and no ECM delay
    print(f"[*] Factoring n = {n} ({len(str(n))} digits, {threads} threads)...")
    cmd = ["./yafu", f"factor({n})", "-threads", str(threads), "-noecm"]
    res = subprocess.run(cmd, cwd=YAFU_DIR, capture_output=True, text=True)
    factors = []
    for line in res.stdout.splitlines():
        for pattern in [r'P\d+\s*=\s*(\d+)', r'prp\d+\s*=\s*(\d+)']:
            m = re.search(pattern, line)
            if m:
                factors.append(int(m.group(1)))
    factors = [f for f in factors if 1 < f < n and n % f == 0]
    if factors:
        p = factors[0]
        q = n // p
        print(f"[+] Factored n = {n}:\n    p = {p}\n    q = {q}")
        return p, q
    raise RuntimeError(f"[-] YAFU failed to factor {n}\nOutput:\n{res.stdout}")

def decrypt_rsa_segment(seg: dict[str, int], threads: int = 12) -> bytes:
    n, e, c = seg['n'], seg['e'], seg['c']
    p, q = factor_n(n, threads=threads)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    return long_to_bytes(m)

def parse_public_segments(file_path: str) -> list[dict[str, int]]:
    """Extracts PUBLIC_SEGMENTS from a python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'PUBLIC_SEGMENTS\s*=\s*(\[[^\]]+\])', content)
    if not m:
        raise ValueError(f"Could not find PUBLIC_SEGMENTS in {file_path}")
    return ast.literal_eval(m.group(1))

def download_remote_files(host: str, port: int, out_dir: str) -> tuple[str, str]:
    """Connects to challenge server and downloads chall.py and chall.zip."""
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.create_connection((host, port), timeout=10)
    banner = s.recv(4096).decode('utf-8', errors='ignore')

    m = re.search(r'http://[^\s]+/download/([a-zA-Z0-9_-]+)/chall\.py', banner)
    if not m:
        s.close()
        raise ValueError(f"Failed to find download token in banner:\n{banner}")
    token = m.group(1)
    url_py = f"http://{host}:{port}/download/{token}/chall.py"
    url_zip = f"http://{host}:{port}/download/{token}/chall.zip"

    py_path = os.path.join(out_dir, "chall.py")
    zip_path = os.path.join(out_dir, "chall.zip")

    try:
        print(f"[*] Downloading {url_py}...")
        urllib.request.urlretrieve(url_py, py_path)
        print(f"[*] Downloading {url_zip}...")
        urllib.request.urlretrieve(url_zip, zip_path)
    finally:
        try:
            s.sendall(b'done\n')
            s.close()
        except Exception:
            pass

    return py_path, zip_path

def extract_archive(zip_path: str, password: str, extract_to: str):
    """Extracts a zip file using 7z."""
    os.makedirs(extract_to, exist_ok=True)
    subprocess.run(["7z", "x", f"-p{password}", zip_path, f"-o{extract_to}", "-y"], check=True, stdout=subprocess.DEVNULL)

def solve(host: str = None, port: int = None):
    os.makedirs(TEMP_DIR, exist_ok=True)

    if host and port:
        print(f"=== Remote mode: {host}:{port} ===")
        chall_py, chall_zip = download_remote_files(host, port, TEMP_DIR)
    else:
        local_py = os.path.join(WORKSPACE_DIR, "challenge/chall.py")
        local_zip = os.path.join(WORKSPACE_DIR, "challenge/chall.zip")
        if os.path.exists(local_py) and os.path.exists(local_zip):
            print("=== Local mode: using existing challenge/ files ===")
            chall_py, chall_zip = local_py, local_zip
        else:
            raise ValueError("No remote host/port provided and local challenge files not found!")

    # Step 1: Solve chall.py -> extract chall.zip
    print("\n--- [Step 1] Decrypting chall.zip password ---")
    segments = parse_public_segments(chall_py)
    chunks = []
    for i, seg in enumerate(segments):
        print(f"[*] Processing segment {i+1}/{len(segments)}...")
        chunks.append(decrypt_rsa_segment(seg, threads=12))
    chall_password = b"".join(chunks).decode('ascii', errors='ignore')
    print(f"[+] chall.zip password: {chall_password}")

    extracted_1 = os.path.join(TEMP_DIR, "extracted_chall")
    extract_archive(chall_zip, chall_password, extracted_1)

    # Step 2: Solve secret.py -> extract secret.zip
    print("\n--- [Step 2] Decrypting secret.zip password ---")
    secret_py = os.path.join(extracted_1, "secret.py")
    secret_zip = os.path.join(extracted_1, "secret.zip")
    segments = parse_public_segments(secret_py)
    chunks = [decrypt_rsa_segment(seg, threads=12) for seg in segments]
    secret_password = b"".join(chunks).decode('ascii', errors='ignore')
    print(f"[+] secret.zip password: {secret_password}")

    extracted_2 = os.path.join(TEMP_DIR, "extracted_secret")
    extract_archive(secret_zip, secret_password, extracted_2)

    # Step 3: Solve flag.py -> extract flag.zip
    print("\n--- [Step 3] Decrypting flag.zip password ---")
    flag_py = os.path.join(extracted_2, "flag.py")
    flag_zip = os.path.join(extracted_2, "flag.zip")
    segments = parse_public_segments(flag_py)
    chunks = [decrypt_rsa_segment(seg, threads=12) for seg in segments]
    flag_password = b"".join(chunks).decode('ascii', errors='ignore')
    print(f"[+] flag.zip password: {flag_password}")

    extracted_3 = os.path.join(TEMP_DIR, "extracted_flag")
    extract_archive(flag_zip, flag_password, extracted_3)

    # Step 4: Read flag.txt
    flag_file = os.path.join(extracted_3, "flag.txt")
    with open(flag_file, "r", encoding="utf-8") as f:
        flag = f.read().strip()

    print("\n" + "=" * 50)
    print(f"[🚩] FLAG: {flag}")
    print("=" * 50)
    return flag

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        solve(sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 2:
        host, port = sys.argv[1].split(":")
        solve(host, int(port))
    else:
        solve()
