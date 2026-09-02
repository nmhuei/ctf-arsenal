#!/usr/bin/env python3
"""Debug: check if candidate pairs are actually conjugate."""
import sys, json, base64, zlib, itertools, hashlib, random, time

N = 32
AAD = b"linchan/v2"
KEY_DOMAIN = b"linchan-v2/key\0"

def rank(rows):
    p = {}
    for x in rows:
        x = int(x)
        while x:
            i = x.bit_length() - 1
            if i in p: x ^= p[i]
            else: p[i] = x; break
    return len(p)

def transpose(a):
    n = len(a)
    out = [0] * n
    for i, row in enumerate(a):
        x = row
        while x:
            j = (x & -x).bit_length() - 1
            out[j] |= 1 << i
            x &= x - 1
    return out

def matmul(a, b):
    bt = transpose(b)
    return [sum(((row & col).bit_count() & 1) << j for j, col in enumerate(bt)) for row in a]

def vec(rows):
    v = 0
    for i, row in enumerate(rows):
        v |= int(row) << (N * i)
    return v

def unvec(v):
    mask = (1 << N) - 1
    return [(v >> (N * i)) & mask for i in range(N)]

def identity(n=N):
    return [1 << i for i in range(n)]

def inverse(a):
    n = len(a)
    aug = [a[i] | (1 << (n + i)) for i in range(n)]
    r = 0
    for c in range(n):
        q = next((q for q in range(r, n) if (aug[q] >> c) & 1), None)
        if q is None: raise ValueError("singular")
        aug[r], aug[q] = aug[q], aug[r]
        for q in range(n):
            if q != r and ((aug[q] >> c) & 1): aug[q] ^= aug[r]
        r += 1
    return [(x >> n) & ((1 << n) - 1) for x in aug]

def _p(S):
    return b"".join(int(x).to_bytes(4, "little") for x in S)

def _f(S):
    Si = inverse(S)
    return min(_p(S), _p(Si), _p(transpose(S)), _p(transpose(Si)))

def _k(S):
    X = b"".join(sorted(_f(A) for A in S))
    return hashlib.shake_256(KEY_DOMAIN + X).digest(32)

def b85(x):
    if isinstance(x, str): x = x.encode()
    return base64.b85decode(x)

def load_output(path):
    raw = open(path, "rb").read().strip()
    try: raw = zlib.decompress(base64.b85decode(raw))
    except: raw = zlib.decompress(base64.a85decode(raw))
    return json.loads(raw)

def decode_space(x):
    raw = b85(x)
    if len(raw) % 128: raise ValueError("bad size")
    return [[int.from_bytes(raw[o + 4*r:o + 4*r + 4], "little") for r in range(N)] for o in range(0, len(raw), 128)]

def rref_basis(vs):
    piv = {}
    for x in vs:
        x = int(x)
        while x:
            p = x.bit_length() - 1
            if p in piv: x ^= piv[p]
            else:
                for q in list(piv):
                    if (piv[q] >> p) & 1: piv[q] ^= x
                piv[p] = x; break
    return [piv[p] for p in sorted(piv, reverse=True)]

def nullspace(rows, ncols):
    rows = [int(x) for x in rows if x]
    rr = []; pivots = []; r = 0
    for c in range(ncols):
        q = next((q for q in range(r, len(rows)) if (rows[q] >> c) & 1), None)
        if q is None: continue
        rows[r], rows[q] = rows[q], rows[r]
        for q in range(len(rows)):
            if q != r and ((rows[q] >> c) & 1): rows[q] ^= rows[r]
        rr.append(rows[r]); pivots.append(c); r += 1
        if r == len(rows): break
    pivot_set = set(pivots); out = []
    for free in range(ncols):
        if free in pivot_set: continue
        x = 1 << free
        for row, p in reversed(list(zip(rr, pivots))):
            if (row & x).bit_count() & 1: x ^= 1 << p
        out.append(x)
    return out

def intertwiner_equations(C, D):
    rows = []
    for A, B in zip(C, D):
        for r in range(N):
            brow = B[r]
            for c in range(N):
                eq = 0
                for k in range(N):
                    if (A[k] >> c) & 1: eq ^= 1 << (r * N + k)
                x = brow
                while x:
                    lb = x & -x; k = lb.bit_length() - 1
                    eq ^= 1 << (k * N + c); x ^= lb
                if eq: rows.append(eq)
    return rows

def solve_intertwiner(C, D):
    ns = nullspace(intertwiner_equations(C, D), N * N)
    if not ns: return None
    candidates = list(ns)
    rng = random.Random(0x1337)
    for _ in range(4096):
        if candidates:
            if _ < len(candidates): x = candidates[_]
            else:
                x = 0
                for b in candidates:
                    if rng.getrandbits(1): x ^= b
        if not x: continue
        S = unvec(x)
        if rank(S) == N: return S
    return None

def conjugate_space(S, C):
    Si = inverse(S)
    return [matmul(matmul(S, A), Si) for A in C]

def same_span(A, B):
    av = rref_basis(map(vec, A))
    bv = rref_basis(map(vec, B))
    return av == bv

def verify_conjugacy(S, C, D):
    try: return same_span(conjugate_space(S, C), D)
    except: return False

def full_rank_hist(space):
    m = len(space); h = {}
    for mask in range(1, 1 << m):
        A = [0] * N
        for i in range(m):
            if (mask >> i) & 1: A = [x ^ y for x, y in zip(A, space[i])]
        r = rank(A); h[r] = h.get(r, 0) + 1
    return tuple(sorted(h.items()))

def elem_inv(A):
    A2 = matmul(A, A)
    A3 = matmul(A2, A)
    return (rank(A), rank(A2), rank(A3))

def combinations(space):
    m = len(space); out = []
    for mask in range(1, 1 << m):
        A = [0] * N
        for i in range(m):
            if (mask >> i) & 1: A = [x ^ y for x, y in zip(A, space[i])]
        out.append((mask, A))
    return out

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "linchan/output.txt"
    obj = load_output(path)
    boxes = []
    for i, box in enumerate(obj["boxes"]):
        boxes.append({"id": i, "m": int(box["m"]), "space": decode_space(box["x"])})

    groups = {}
    for box in boxes:
        groups.setdefault(box["m"], []).append(box)

    # For m=16, find all pairs with matching full rank hist
    for m in [16]:
        G = groups.get(m, [])
        buckets = {}
        for box in G:
            inv = full_rank_hist(box["space"])
            buckets.setdefault(inv, []).append(box)

        print(f"m={m}: {len(G)} boxes, {len(buckets)} buckets")
        candidate_pairs = []
        for bucket in buckets.values():
            if len(bucket) >= 2:
                candidate_pairs.extend(itertools.combinations(bucket, 2))

        print(f"  {len(candidate_pairs)} candidate pairs")

        # For each candidate pair, check how many elements match by (rank, rank^2, rank^3)
        for a, b in candidate_pairs[:5]:
            t0 = time.time()
            CC = combinations(a["space"])
            DD = combinations(b["space"])

            inv_c = {}
            inv_d = {}
            for _, A in CC:
                inv = elem_inv(A)
                inv_c.setdefault(inv, []).append(A)
            for _, A in DD:
                inv = elem_inv(A)
                inv_d.setdefault(inv, []).append(A)

            common = set(inv_c.keys()) & set(inv_d.keys())
            unique_matches = sum(1 for k in common if len(inv_c[k]) == 1 and len(inv_d[k]) == 1)
            total_matched = sum(min(len(inv_c[k]), len(inv_d[k])) for k in common)
            total_unmatched_c = sum(len(v) for k, v in inv_c.items() if k not in common)
            total_unmatched_d = sum(len(v) for k, v in inv_d.items() if k not in common)

            elapsed = time.time() - t0
            print(f"  Pair ({a['id']}, {b['id']}): {len(common)} common invs, "
                  f"{unique_matches} unique matches, "
                  f"{total_matched}/{len(CC)} matched, "
                  f"unmatched_c={total_unmatched_c}, unmatched_d={total_unmatched_d} "
                  f"({elapsed:.1f}s)")

            # Quick recovery test with just unique matches
            base_c, base_d = [], []
            for inv in common:
                if len(inv_c[inv]) == 1 and len(inv_d[inv]) == 1:
                    base_c.append(inv_c[inv][0])
                    base_d.append(inv_d[inv][0])

            if len(base_c) >= 3:
                print(f"    Trying with {len(base_c)} unique matches...")
                S = solve_intertwiner(base_c[:10], base_d[:10])
                if S is not None:
                    v = verify_conjugacy(S, a["space"], b["space"])
                    print(f"    solve OK, verify: {v}")
                    if v:
                        print(f"    *** FOUND S for ({a['id']}, {b['id']})!")
                else:
                    print(f"    solve_intertwiner returned None")

if __name__ == "__main__":
    main()
