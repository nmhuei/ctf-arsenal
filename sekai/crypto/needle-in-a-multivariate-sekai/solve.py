#!/usr/bin/env sage -python
import os
import ast
import time
import random as pyrandom
import multiprocessing as mp
from hashlib import sha256
from sage.all import *
from sage.quadratic_forms.quadratic_form import QuadraticForm

BASE = "crypto_needle-in-a-multivariate-sekai"
N = 144
TARGET_MSG = b"STAGE OF SEKAI"

# tăng nếu máy khỏe
PARI_STACK = 2**30

# subform rank nhỏ chạy nhanh hơn; rank lớn dễ có nghiệm hơn nhưng qfsolve nặng hơn
RANKS = [5, 6, 7, 8, 9, 10]

# mỗi qfsolve bị giới hạn thời gian bằng process riêng
TIMEOUT_PER_TRY = 8

# số attempt tổng
MAX_TRIES = 20000

# ưu tiên lấy index có diag nhỏ
POOL_SIZE = 80

def H(m: bytes):
    return Integer(int.from_bytes(b"\x01" + sha256(m).digest(), "big"))

def qform(M, v):
    return Integer(v * M * v)

def build_Q_from_submatrix(A, idx):
    """
    Sage QuadraticForm convention:
      coeff diag = A[i,i]
      coeff offdiag = 2*A[i,j]
    để Q(x) == x.T * A_sub * x
    """
    m = len(idx)
    coeff = []
    for a in range(m):
        i = idx[a]
        coeff.append(ZZ(A[i, i]))
        for b in range(a + 1, m):
            j = idx[b]
            coeff.append(ZZ(2 * A[i, j]))
    return QuadraticForm(QQ, m, [QQ(c) for c in coeff])

def qsolve_worker(A_list, idx, target, q_out):
    """
    Worker riêng để nếu PARI/qfsolve treo thì parent kill process.
    """
    try:
        pari.allocatemem(PARI_STACK)

        m = len(idx)
        A = matrix(ZZ, A_list)

        Q = build_Q_from_submatrix(A, idx)
        sol = Q.solve(QQ(target))

        den = lcm([QQ(c).denominator() for c in sol])
        if den != 1:
            q_out.put(("rational", int(ZZ(den).nbits()), None))
            return

        sol = [ZZ(c) for c in sol]

        # verify trong worker
        val = Q(vector(ZZ, sol))
        if val == target:
            q_out.put(("integer", 0, sol))
        else:
            q_out.put(("bad", int(val - target), sol))

    except Exception as e:
        q_out.put(("fail", repr(e), None))

def try_qsolve(A, idx, target, timeout=TIMEOUT_PER_TRY):
    q_out = mp.Queue()
    A_list = [[ZZ(A[i, j]) for j in range(N)] for i in range(N)]

    p = mp.Process(target=qsolve_worker, args=(A_list, idx, ZZ(target), q_out))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return ("timeout", None, None)

    if q_out.empty():
        return ("empty", None, None)

    return q_out.get()

def verify_samples(pk):
    with open("output.txt", "r") as f:
        sigs = ast.literal_eval(f.read())

    ok = 0
    for i, s in enumerate(sigs):
        v = vector(ZZ, s)
        t = H(f"message {i}".encode())
        if qform(pk, v) != t:
            print("[-] bad sample", i)
            print("    diff =", qform(pk, v) - t)
            raise SystemExit
        ok += 1

    print(f"[+] sample verify: {ok}/{len(sigs)}")

def main():
    os.chdir(BASE)

    pk_data = load("pk.sobj")
    pk = pk_data["pk"]
    target = H(TARGET_MSG)

    print("[+] params:", pk_data["params"])
    print("[+] pk dims:", pk.dimensions())
    print("[+] target =", hex(int(target)))

    verify_samples(pk)

    print("[+] qflllgram reducing...")
    R = matrix(ZZ, pari.qflllgram(pari(pk)))
    A = R.T * pk * R

    print("[+] det(R) =", R.det())
    print("[+] reduced diag bits:",
          min(A[i, i].nbits() for i in range(N)),
          max(A[i, i].nbits() for i in range(N)))

    # pool: các tọa độ có diagonal nhỏ nhất
    sorted_idx = sorted(range(N), key=lambda i: A[i, i])
    pool = sorted_idx[:POOL_SIZE]

    print("[+] pool size =", len(pool))
    print("[+] pool diag bit range:",
          min(A[i, i].nbits() for i in pool),
          max(A[i, i].nbits() for i in pool))

    start = time.time()
    seen = set()

    for attempt in range(1, MAX_TRIES + 1):
        r = pyrandom.choice(RANKS)

        # mix: 70% chọn từ diag nhỏ, 30% chọn full random
        if pyrandom.random() < 0.70:
            idx = sorted(pyrandom.sample(pool, r))
        else:
            idx = sorted(pyrandom.sample(range(N), r))

        key = tuple(idx)
        if key in seen:
            continue
        seen.add(key)

        print(f"\n[+] attempt {attempt}/{MAX_TRIES} rank={r} idx={idx}", flush=True)

        status, info, sol = try_qsolve(A, idx, target)

        print("[+] qsolve status:", status, info, flush=True)

        if status != "integer":
            continue

        y = vector(ZZ, [0] * N)
        for pos, coeff in zip(idx, sol):
            y[pos] = ZZ(coeff)

        diff_reduced = qform(A, y) - target
        print("[+] reduced diff =", diff_reduced, flush=True)

        if diff_reduced != 0:
            continue

        sig = R * y
        diff_public = qform(pk, sig) - target
        print("[+] public diff =", diff_public, flush=True)

        if diff_public == 0:
            print("\n[FOUND] exact signature")
            print("[+] q(sig)-target = 0")
            print("[+] elapsed =", round(time.time() - start, 2), "sec")

            with open("solution_space.txt", "w") as f:
                f.write(" ".join(map(str, sig)))

            with open("solution_list.txt", "w") as f:
                f.write(str(list(map(int, sig))))

            print("[+] wrote solution_space.txt")
            print("[+] wrote solution_list.txt")
            print("[+] send format: whitespace integers")
            print(" ".join(map(str, sig)))
            return

    print("[-] not found")
    print("[!] tăng MAX_TRIES, TIMEOUT_PER_TRY hoặc thêm rank 11/12 nếu cần")

if __name__ == "__main__":
    main()
