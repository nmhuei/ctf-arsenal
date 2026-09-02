#!/usr/bin/env python3
import itertools
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "files" / "data_8067cb731187767faec8c856d097645d.json"
ED = ROOT / "files" / "ed25519_47f2b0b21c6de8177aa298f1b91bf525.py"

spec = importlib.util.spec_from_file_location("ed25519", ED)
ed25519 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ed25519)


def aes_cbc_decrypt(key: bytes, iv: bytes, ct: bytes) -> bytes:
    try:
        from Crypto.Cipher import AES
        return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    except ImportError:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        return dec.update(ct) + dec.finalize()


def likely_flag(pt: bytes) -> bool:
    return (pt.startswith(b"ECSC{") or pt.startswith(b"crypto{") or pt.startswith(b"flag{")) and pt.rstrip().endswith(b"}")


def main():
    data = json.loads(DATA.read_text())

    # ring_sign() uses random 256-bit numbers for fake entries, but for the real signer it reduces
    # both c_i and r_i modulo the Ed25519 subgroup order l. Therefore the real index is normally
    # the unique position where both signature integers are < l. If a fake entry is also small by
    # chance, brute-force the tiny ambiguity and test AES plaintext.
    choices = []
    for level_no, level in enumerate(data["levels"]):
        _, sigc, sigr = level["signature"]
        cand = [i for i, (c, r) in enumerate(zip(sigc, sigr)) if c < ed25519.l and r < ed25519.l]
        print(f"level {level_no:02d}: candidates = {cand}")
        choices.append(cand)

    iv = bytes.fromhex(data["iv"])
    ct = bytes.fromhex(data["enc"])

    for idxs in itertools.product(*choices):
        key_hex = "".join(data["levels"][j]["public_keys"][i][:2] for j, i in enumerate(idxs))
        key = bytes.fromhex(key_hex)
        pt = aes_cbc_decrypt(key, iv, ct)
        print(f"try {idxs}: key={key.hex()} pt={pt!r}")
        if likely_flag(pt):
            print("\nFLAG:", pt.decode())
            return

    print("No flag-looking plaintext found")


if __name__ == "__main__":
    main()
