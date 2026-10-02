#!/usr/bin/env python3
# Solution for: From Update To Encrypt (Forensics) - CSCV 2026 Quals
# Chain: update.exe (AES-256-GCM, BCrypt) encrypts 7 files in C:\\Users\\Public\\MetaData\\Data
# File format: b'1337DaKL' + tag(16) + ciphertext (nonce NOT stored)
# Key = SHA256("desktop-7nnknik|2844|X7A91C"):
#   computer DESKTOP-7NNKNIK (sysmon/GetComputerNameA, lowercased by binary),
#   PID 2844 (sysmon EventID 1 for update.exe),
#   campaign X7A91C (pcap 192.168.56.1:8080/api/check -> {"campaign":"X7A91C","status":"ok"})
#   (confirmed via Ghidra decompile of main: KDF string = lower(computer)|PID|campaign)
# Per-file 12B nonce from BCryptGenRandom (NOT in files) -> recovered from
# update.exe thread stack in mem.raw (volatility vad dump pid.2844 0xd30000 region).
import argparse, hashlib, pathlib
from Crypto.Cipher import AES

KEY = hashlib.sha256(b"desktop-7nnknik|2844|X7A91C").digest()
NONCES = {
    # recovered from update.exe stack (mem.raw -> vol vadinfo --pid 2844 --dump)
    "hi.txt.enc": "24c696f9341fd8e7882b44f0",
    "1337dakl.txt.enc": "f13ba19b255ae4f590c25cfd",
    "ptit.txt.enc": "adea20882fde1b4d6e74f57c",
    "flag.jpeg.enc": "97595686149cf7a4afe5cd6f",
    "IMG_4287.jpeg.enc": "5a3ea1093656db3093d8df16",
}
BASE = pathlib.Path(__file__).resolve().parents[1]

def decrypt(enc_path):
    d = pathlib.Path(enc_path).read_bytes()
    assert d[:8] == b"1337DaKL", "bad magic"
    tag, ct = d[8:24], d[24:]
    nonce = bytes.fromhex(NONCES[pathlib.Path(enc_path).name])
    return AES.new(KEY, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--encdir", default=str(BASE/"script"/"x"/"Users"/"Public"/"MetaData"/"Data"))
    a = ap.parse_args()
    for name in NONCES:
        pt = decrypt(str(pathlib.Path(a.encdir)/name))
        print(f"{name} -> {pt[:60]!r}")

if __name__ == "__main__":
    main()
