#!/usr/bin/env python3
import subprocess
import re
import os
import sys
from Crypto.Util.number import long_to_bytes

yafu_bin = "/home/light/Workspace/CTF/PTIT_CTF_2026/Crypto/CIA_-_What_does_I_stand_for/script/yafu_src/yafu"

segments = [
    {'n': 809202123321579685401617788106445594231775612578151779805866771945418402394099133599, 'e': 65537, 'c': 89861711489775304931802240968890454801139611958195184925558489444519115858076894318, 'p': 880913373141544439500247670685313272172483, 'q': 918594436176822293291401133943140556824053},
    {'n': 803855454786320296632238674906141081938111250236884983107257253200573075747010995897, 'e': 65537, 'c': 219667971674321047373978993461033713949014654436338912885172730779544603069845628096},
    {'n': 1374897230920489386987957111300125246071865030443987463188362271527034943605714958641, 'e': 65537, 'c': 904681635993209962901941749935599730648335967672080253648969091354019623013252442937},
    {'n': 568864255617218463757762331562162938196758766213517971897386306909128571711714362993, 'e': 65537, 'c': 37007777510121720696560883010496856261737978467877192747323372316738381125311145311}
]

def factor_with_yafu(n):
    print(f"[*] Factoring {n} with YAFU (12 threads)...")
    res = subprocess.run([yafu_bin, f"factor({n})", "-threads", "12"], capture_output=True, text=True)
    factors = []
    for line in res.stdout.splitlines():
        m = re.search(r'P\d+\s*=\s*(\d+)', line)
        if m:
            factors.append(int(m.group(1)))
        m2 = re.search(r'prp\d+\s*=\s*(\d+)', line)
        if m2:
            factors.append(int(m2.group(1)))
    factors = [f for f in factors if 1 < f < n and n % f == 0]
    if factors:
        p = factors[0]
        q = n // p
        return p, q
    raise RuntimeError(f"YAFU failed to factor {n}\nOutput:\n{res.stdout}")

if __name__ == '__main__':
    chunks = []
    for i, seg in enumerate(segments):
        n, e, c = seg['n'], seg['e'], seg['c']
        if 'p' in seg:
            p, q = seg['p'], seg['q']
        else:
            p, q = factor_with_yafu(n)
        print(f"[+] Segment {i} factors: p={p}, q={q}")
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(c, d, n)
        chunk = long_to_bytes(m)
        print(f"[+] Segment {i} decrypted: {chunk}")
        chunks.append(chunk)

    full_password = b"".join(chunks)
    print(f"\n[+] FULL PASSWORD: {full_password.decode('ascii', errors='ignore')}")
