#!/usr/bin/env python3
import importlib.util
import json
import os
import sys
import time
from collections import defaultdict

import galois
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(
    ROOT,
    "challenge",
    "less_is_more_c21e39cc296efe86ee76902cae855a705bd74214",
    "less_is_more",
)
spec = importlib.util.spec_from_file_location("chall", os.path.join(BASE, "challenge.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
data = json.load(open(os.path.join(BASE, "output.txt"), encoding="utf-8"))

sys.path.insert(0, HERE)
import match_known_v as mk  # noqa: E402

GF = galois.GF(c.q)
k, n = c.k, c.n


def full_generator(right):
    G = np.zeros((k, n), dtype=np.int64)
    G[:, :k] = np.eye(k, dtype=np.int64)
    G[:, k:] = np.asarray(right, dtype=np.int64)
    return G


G0 = full_generator(data["G0"])
PUB = [full_generator(P) for P in data["PK"]]


def systematic_right(G, J):
    J = np.asarray(sorted(map(int, J)), dtype=np.int64)
    mask = np.ones(n, dtype=bool)
    mask[J] = False
    K = np.arange(n, dtype=np.int64)[mask]
    X = GF(G[:, J])
    B = np.linalg.inv(X) @ GF(G[:, K])
    return np.asarray(B, dtype=np.int64)


def zero_fp(B):
    Z = B == 0
    rd = tuple(sorted(map(int, Z.sum(axis=1))))
    cd = tuple(sorted(map(int, Z.sum(axis=0))))
    rdeg = Z.sum(axis=1)
    cdeg = Z.sum(axis=0)
    r2 = tuple(sorted(tuple(sorted(map(int, cdeg[np.flatnonzero(Z[i])])))
                      for i in range(k)))
    c2 = tuple(sorted(tuple(sorted(map(int, rdeg[np.flatnonzero(Z[:, j])])))
                      for j in range(k)))
    return rd, cd, r2, c2


src = list(mk.known)
rsp = []
for ti, tx in enumerate(data["tx"]):
    b = c.sch(bytes.fromhex(tx["cmt"]))
    ri = 0
    for pos, bi in enumerate(b):
        if not bi:
            continue
        rsp.append((ti, pos, bi, ri, tuple(tx["rsp"][ri])))
        ri += 1

print(f"source={len(src)} responses={len(rsp)}")
start = time.time()
src_map = defaultdict(list)
for idx, (S, ti, pos) in enumerate(src, 1):
    B = systematic_right(G0, S)
    src_map[zero_fp(B)].append((ti, pos, S))
    if idx % 25 == 0:
        print(f"source progress {idx}/{len(src)} elapsed={time.time()-start:.1f}s", flush=True)

matches = []
for idx, (ti, pos, bi, ri, J) in enumerate(rsp, 1):
    B = systematic_right(PUB[bi - 1], J)
    fp = zero_fp(B)
    if fp in src_map:
        for rec in src_map[fp]:
            matches.append(((ti, pos, bi, ri, J), rec))
    if idx % 25 == 0:
        print(f"rsp progress {idx}/{len(rsp)} elapsed={time.time()-start:.1f}s matches={len(matches)}", flush=True)

print("MATCHES", len(matches))
for m in matches:
    a, b = m
    print("rsp", a[:4], "source", b[:2])
print(f"elapsed={time.time()-start:.1f}s")
