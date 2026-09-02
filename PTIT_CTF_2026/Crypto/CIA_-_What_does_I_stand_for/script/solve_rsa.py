#!/usr/bin/env python3
import subprocess
import multiprocessing as mp
import random
import re
import os
import signal
import sys
import time
from Crypto.Util.number import long_to_bytes

ecm_bin = "/home/light/Workspace/CTF/PTIT_CTF_2026/Crypto/CIA_-_What_does_I_stand_for/script/ecm_src/ecm"

def worker(n, b1, start_sigma, count, result_queue, stop_event):
    cmd = [ecm_bin, "-sigma", str(start_sigma), "-c", str(count), str(b1)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, _ = p.communicate(input=f"{n}\n")
        for line in out.splitlines():
            if "factor found" in line or "Factor found" in line:
                m = re.search(r'factor found.*:\s*(\d+)', line, re.IGNORECASE)
                if m:
                    fac = int(m.group(1))
                    if 1 < fac < n:
                        result_queue.put(fac)
                        stop_event.set()
                        return
    except Exception:
        pass
    finally:
        if p.poll() is None:
            p.kill()

def factor_n(n, num_workers=12):
    for b1, curves in [(1000000, 30), (2500000, 40), (5000000, 50)]:
        print(f"Factoring {n} with {num_workers} parallel ECM workers (B1={b1}, {curves} curves each)...")
        result_queue = mp.Queue()
        stop_event = mp.Event()
        processes = []
        for i in range(num_workers):
            start_sigma = random.randint(1, 2000000000)
            p = mp.Process(target=worker, args=(n, b1, start_sigma, curves, result_queue, stop_event))
            p.start()
            processes.append(p)
        
        # Wait with timeout
        start_time = time.time()
        timeout = curves * 3.5 # seconds
        fac = None
        while time.time() - start_time < timeout:
            try:
                fac = result_queue.get(timeout=1.0)
                if fac:
                    break
            except Exception:
                if not any(p.is_alive() for p in processes):
                    break
        
        stop_event.set()
        for p in processes:
            if p.is_alive():
                p.terminate()
            p.join()
        
        if fac:
            print(f"Found factor: {fac}")
            return fac
    raise RuntimeError(f"Failed to factor {n}")

segments = [
    {'n': 809202123321579685401617788106445594231775612578151779805866771945418402394099133599, 'e': 65537, 'c': 89861711489775304931802240968890454801139611958195184925558489444519115858076894318},
    {'n': 803855454786320296632238674906141081938111250236884983107257253200573075747010995897, 'e': 65537, 'c': 219667971674321047373978993461033713949014654436338912885172730779544603069845628096},
    {'n': 1374897230920489386987957111300125246071865030443987463188362271527034943605714958641, 'e': 65537, 'c': 904681635993209962901941749935599730648335967672080253648969091354019623013252442937},
    {'n': 568864255617218463757762331562162938196758766213517971897386306909128571711714362993, 'e': 65537, 'c': 37007777510121720696560883010496856261737978467877192747323372316738381125311145311}
]

if __name__ == '__main__':
    chunks = []
    for i, seg in enumerate(segments):
        n, e, c = seg['n'], seg['e'], seg['c']
        p = factor_n(n, num_workers=12)
        q = n // p
        assert p * q == n
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(c, d, n)
        chunk = long_to_bytes(m)
        print(f"Segment {i} decrypted: {chunk}")
        chunks.append(chunk)

    full_password = b"".join(chunks)
    print(f"FULL PASSWORD: {full_password.decode('ascii', errors='ignore')}")
