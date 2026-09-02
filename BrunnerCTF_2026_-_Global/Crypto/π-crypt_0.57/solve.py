#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime, timezone

BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789æøåÆØÅ .,!?-:()[]/{}=<>+_@^|~%$#&*`“';"
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "crypto_pi-crypt-0-57"
PROGRESS = Path("/home/light/GitHub/gpt/scratch/ctf-runs/pi-crypt-057/progress.json")

def idxs(s):
    return [BASE.index(c) for c in s]

def chars(vals):
    return "".join(BASE[v % len(BASE)] for v in vals)

def pie_crypt(text: str, key: str, decrypt: bool = False) -> str:
    pie = (DATA / "unbaked_pi.txt").read_text(encoding="utf-8")
    out = ""
    i = sum(BASE.index(c) for c in key)
    j = 0
    for c in text:
        d1 = int(pie[i % len(pie)])
        i += BASE.index(key[j % len(key)])
        j += 1
        d2 = int(pie[i % len(pie)])
        i += BASE.index(key[j % len(key)])
        j += 1
        shift = 10 * d1 + d2
        out += BASE[(BASE.index(c) + (-shift if decrypt else shift)) % len(BASE)]
    return out

def solve():
    ct = (DATA / "baked_pie.txt").read_text(encoding="utf-8").rstrip("\n")
    n = len(ct) // 4
    c0, c1, c2, c3 = [idxs(ct[i*n:(i+1)*n]) for i in range(4)]

    # The 16-round custom ingredient is linear over Z_100:
    # out0=33K, out1=54K, out2=13L+21R+33K, out3=21L+34R+54K.
    inv33 = pow(33, -1, 100)
    k = [(inv33 * x) % 100 for x in c0]
    assert c1 == [(54 * x) % 100 for x in k], "key consistency check failed"

    a = [(c2[i] - 33 * k[i]) % 100 for i in range(n)]
    b = [(c3[i] - 54 * k[i]) % 100 for i in range(n)]

    # inverse of [[13,21],[21,34]] modulo 100 has determinant 1:
    left = [(34 * a[i] - 21 * b[i]) % 100 for i in range(n)]
    right = [(-21 * a[i] + 13 * b[i]) % 100 for i in range(n)]

    key = chars(k)
    baked_stage = chars(left + right)
    flag = pie_crypt(baked_stage, key, decrypt=True)

    assert len(key) == 64
    assert flag.startswith("brunner{") and flag.endswith("}"), flag

    (ROOT / "flag.txt").write_text(flag + "\n", encoding="utf-8")
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps({
        "challenge": "π-crypt 0.57",
        "status": "solved",
        "workspace": str(ROOT),
        "artifact_dir": str(DATA),
        "method": "inverted linearized 16-round custom Feistel ingredient, recovered 64-char key, then decrypted pie_crypt",
        "key": key,
        "flag": flag,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"FLAG: {flag}")

if __name__ == "__main__":
    solve()
