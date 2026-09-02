#!/usr/bin/env python3
import importlib.util
import json
import math
import os
import struct
import sys
import time
from collections import defaultdict
from multiprocessing import Pool, cpu_count

import galois
import numpy as np
from numba import njit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(
    ROOT, "challenge",
    "less_is_more_c21e39cc296efe86ee76902cae855a705bd74214",
    "less_is_more",
)
spec = importlib.util.spec_from_file_location("chall", os.path.join(BASE, "challenge.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
data = json.load(open(os.path.join(BASE, "output.txt"), encoding="utf-8"))
q, k, n = c.q, c.k, c.n
M0 = np.asarray(data["G0"], dtype=np.int64)
TARGET_TX = int(sys.argv[1]) if len(sys.argv) > 1 else None

INV = np.zeros(q, dtype=np.int16)
for a in range(1, q):
    INV[a] = pow(int(a), -1, q)

C = np.zeros((n, k), dtype=np.int16)
for i in range(k):
    C[i, i] = 1
C[k:] = M0.T.astype(np.int16)

@njit
def greedy_basis(C, perm, inv):
    nn, kk = C.shape
    basis = np.zeros((kk, kk), dtype=np.int16)
    has = np.zeros(kk, dtype=np.uint8)
    selected = np.empty(kk, dtype=np.int16)
    rnk = 0
    for idx in range(nn):
        ci = perm[idx]
        v = C[ci].copy()
        for r in range(kk):
            if has[r] and v[r] != 0:
                f = v[r]
                for cc in range(r, kk):
                    v[cc] = (v[cc] - f * basis[r, cc]) % 127
        pr = -1
        for r in range(kk):
            if v[r] != 0:
                pr = r
                break
        if pr >= 0:
            iv = inv[v[pr]]
            for cc in range(pr, kk):
                basis[pr, cc] = (v[cc] * iv) % 127
            has[pr] = 1
            selected[rnk] = ci
            rnk += 1
            if rnk == kk:
                break
    return selected

# compile numba before scanning
_ = greedy_basis(C, np.arange(n, dtype=np.int16), INV)

def block_deg(right, V):
    GF = galois.GF(q)
    right = np.asarray(right, dtype=np.int64)
    V = np.asarray(sorted(map(int, V)), dtype=np.int64)
    S = V[V < k]
    T = V[V >= k] - k
    sset = set(map(int, S))
    tset = set(map(int, T))
    R = np.asarray([i for i in range(k) if i not in sset], dtype=np.int64)
    U = np.asarray([i for i in range(k) if i not in tset], dtype=np.int64)
    B = GF(right[np.ix_(S, T)])
    D = GF(right[np.ix_(R, T)])
    Di = np.linalg.inv(D)
    topI = -(B @ Di)
    botI = Di
    MRU = GF(right[np.ix_(R, U)])
    topM = GF(right[np.ix_(S, U)]) - B @ Di @ MRU
    botM = Di @ MRU
    Z = np.asarray(np.block([[topI, topM], [botI, botM]])) == 0
    return (
        tuple(sorted(map(int, Z.sum(axis=1)))),
        tuple(sorted(map(int, Z.sum(axis=0)))),
    )

def rsp_records():
    out = []
    for ti, tx in enumerate(data["tx"]):
        if TARGET_TX is not None and ti != TARGET_TX:
            continue
        b = c.sch(bytes.fromhex(tx["cmt"]))
        ri = 0
        for pos, bi in enumerate(b):
            if bi:
                out.append((ti, pos, bi, ri, tuple(tx["rsp"][ri])))
                ri += 1
    return out

def make_candidates():
    out = []
    for ti, tx in enumerate(data["tx"]):
        if TARGET_TX is not None and ti != TARGET_TX:
            continue
        salt = bytes.fromhex(tx["salt"])
        leaf_seeds = []
        for raw_v, raw_h in tx["path"]:
            source_v = int(raw_v)
            frontier = [(source_v, bytes.fromhex(raw_h))]
            while frontier:
                vv, sd = frontier.pop()
                if vv >= c.lvs:
                    leaf_seeds.append((source_v, sd))
                    continue
                left, right = c.kid(sd)
                frontier.append((2 * vv + 1, right))
                frontier.append((2 * vv, left))
        b = c.sch(bytes.fromhex(tx["cmt"]))
        for pos, bi in enumerate(b):
            if not bi:
                continue
            for v, sd in leaf_seeds:
                Qt = c.spm(c.st_of(sd, salt, struct.pack("<I", pos)), n)
                V = tuple(sorted(map(int, greedy_basis(
                    C, np.asarray(Qt[0], dtype=np.int16), INV
                ))))
                out.append((ti, pos, bi, v, V))
    return out

# Child globals
_W_M0 = None
def init_worker():
    global _W_M0
    _W_M0 = M0

def worker(item):
    ti, pos, bi, v, V = item
    try:
        return (block_deg(_W_M0, V), ti, pos, bi, v, V)
    except np.linalg.LinAlgError:
        return (None, ti, pos, bi, v, V)

def main():
    start = time.time()
    # Target signatures for every captured response.
    target = defaultdict(list)
    for idx, (ti, pos, bi, ri, R) in enumerate(rsp_records(), 1):
        target[block_deg(data["PK"][bi - 1], R)].append((ti, pos, bi, ri, R))
        if idx % 50 == 0:
            print(f"target {idx} elapsed={time.time()-start:.1f}s", flush=True)

    cand = make_candidates()
    print(f"candidates={len(cand)} targets={sum(map(len,target.values()))}", flush=True)
    procs = min(8, max(1, cpu_count() or 1))
    hits = []
    with Pool(procs, initializer=init_worker) as pool:
        for idx, got in enumerate(pool.imap_unordered(worker, cand, chunksize=8), 1):
            sig, ti, pos, bi, v, V = got
            if sig is not None and sig in target:
                # same tx/key/response position is required; otherwise it is just
                # an accidental degree-signature collision.
                for rr in target[sig]:
                    if rr[0] == ti and rr[1] == pos and rr[2] == bi:
                        hits.append((ti, pos, bi, v, V, rr[3], rr[4]))
                        print("HIT", ti, pos, bi, "seed_node", v, "rsp_idx", rr[3], flush=True)
            if idx % 500 == 0:
                print(f"scan {idx}/{len(cand)} elapsed={time.time()-start:.1f}s hits={len(hits)}", flush=True)
    print("FINAL_HITS", len(hits))
    for h in hits:
        print("HIT_DETAIL", h[:4], "V_head", h[4][:12], "R_head", h[6][:12])
    print("elapsed", round(time.time()-start, 2))

if __name__ == "__main__":
    main()
