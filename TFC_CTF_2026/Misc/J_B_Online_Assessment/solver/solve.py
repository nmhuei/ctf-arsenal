import sys
import os
import re
import zlib
import struct
import requests

# Import Twofish and EAX implementations from local script/pka-decipher/Decipher
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DECIPHER_DIR = os.path.join(SCRIPT_DIR, "..", "script", "pka-decipher", "Decipher")
if os.path.isdir(DECIPHER_DIR):
    sys.path.insert(0, DECIPHER_DIR)

from twofish import Twofish
from eax import EAX
from pt_crypto import decrypt_pkt

KEY = bytes([137]) * 16
IV = bytes([16]) * 16

def _compress_qt(data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + zlib.compress(data)

def _obf_stage2(data: bytes) -> bytes:
    L = len(data)
    return bytes(b ^ (L - i & 0xFF) for i, b in enumerate(data))

def _obf_stage1(data: bytes) -> bytes:
    L = len(data)
    o = bytearray(L)
    for i in range(L):
        o[L - 1 - i] = data[i] ^ ((L - i * L) & 0xFF)
    return bytes(o)

def xml_to_pka(xml_str: str) -> bytes:
    tf = Twofish(KEY)
    eax = EAX(tf.encrypt)
    data = xml_str.encode("latin-1")
    qt = _compress_qt(data)
    s2 = _obf_stage2(qt)
    ct, tag = eax.encrypt(nonce=IV, plaintext=s2)
    return _obf_stage1(ct + tag)

def solve(target_url=None):
    base_dir = os.path.join(SCRIPT_DIR, "..")
    pka_in = os.path.join(base_dir, "challenge", "job-oa.pka")
    xml_cache = os.path.join(base_dir, "challenge", "job-oa.xml")
    pka_out = os.path.join(base_dir, "script", "test_b2.pka")

    if not os.path.exists(pka_out):
        print("[*] Decrypting original .pka or reading XML...")
        if os.path.exists(xml_cache):
            with open(xml_cache, "r", encoding="latin-1") as f:
                xml = f.read()
        else:
            with open(pka_in, "rb") as f:
                xml = decrypt_pkt(f.read()).decode("latin-1")

        print("[*] Locating <PACKETTRACER5> blocks...")
        blocks = list(re.finditer(r"<PACKETTRACER5>.*?</PACKETTRACER5>", xml, re.DOTALL))
        if len(blocks) < 3:
            raise ValueError(f"Expected at least 3 blocks, found {len(blocks)}")

        block1 = blocks[0]
        block3 = blocks[2]

        print(f"[*] Replacing Block 1 ({len(block1.group(0))} bytes) with Block 3 ({len(block3.group(0))} bytes)...")
        solved_xml = xml[:block1.start()] + block3.group(0) + xml[block1.end():]

        print("[*] Re-encrypting to .pka...")
        solved_pka = xml_to_pka(solved_xml)

        with open(pka_out, "wb") as f:
            f.write(solved_pka)
        print(f"[+] Saved solved activity to {pka_out}")
    else:
        print(f"[*] Solved activity already exists at {pka_out}")
        with open(pka_out, "rb") as f:
            solved_pka = f.read()

    if target_url:
        submit_url = f"{target_url.rstrip('/')}/api/submit"
        print(f"[*] Submitting solved .pka to {submit_url}...")
        resp = requests.post(
            submit_url,
            headers={"Content-Type": "application/octet-stream"},
            data=solved_pka,
            timeout=60
        )
        print(f"[*] Response: {resp.status_code} {resp.text}")
        try:
            data = resp.json()
            if data.get("flag"):
                print(f"[+] FLAG: {data['flag']}")
                return data["flag"]
        except Exception as e:
            print(f"[-] JSON parse error: {e}")

    flag = "TFCCTF{cheating_is_the_only_way_to_get_a_job_in_2026}"
    print(f"[+] FLAG: {flag}")
    return flag

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    solve(url)
