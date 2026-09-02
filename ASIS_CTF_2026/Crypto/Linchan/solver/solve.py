#!/usr/bin/env python3
import base64
import hashlib
import itertools
import json
import random
import sys
import zlib

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


N = 32
AAD = b"linchan/v2"
KEY_DOMAIN = b"linchan-v2/key\0"


# ---------------------------------------------------------------------------
# GF(2) matrix representation
#
# A matrix is a list of N integers.  Row i is encoded as an N-bit integer.
# ---------------------------------------------------------------------------

def rank(rows):
    p = {}
    for x in rows:
        x = int(x)
        while x:
            i = x.bit_length() - 1
            if i in p:
                x ^= p[i]
            else:
                p[i] = x
                break
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
    return [
        sum(((row & col).bit_count() & 1) << j
            for j, col in enumerate(bt))
        for row in a
    ]


def identity(n=N):
    return [1 << i for i in range(n)]


def inverse(a):
    n = len(a)
    aug = [a[i] | (1 << (n + i)) for i in range(n)]

    r = 0
    for c in range(n):
        q = next((q for q in range(r, n) if (aug[q] >> c) & 1), None)
        if q is None:
            raise ValueError("singular")

        aug[r], aug[q] = aug[q], aug[r]

        for q in range(n):
            if q != r and ((aug[q] >> c) & 1):
                aug[q] ^= aug[r]

        r += 1

    return [(x >> n) & ((1 << n) - 1) for x in aug]


def vec(rows):
    v = 0
    for i, row in enumerate(rows):
        v |= int(row) << (N * i)
    return v


def unvec(v):
    mask = (1 << N) - 1
    return [(v >> (N * i)) & mask for i in range(N)]


# ---------------------------------------------------------------------------
# Challenge canonicalisation / key derivation
# ---------------------------------------------------------------------------

def _p(S):
    """
    Exact binary serialization used for canonicalising a 32x32 GF(2)
    matrix: row-major, 32 rows, four bytes per row.
    """
    return b"".join(int(x).to_bytes(4, "little") for x in S)


def _f(S):
    Si = inverse(S)
    return min(
        _p(S),
        _p(Si),
        _p(transpose(S)),
        _p(transpose(Si)),
    )


def _k(S):
    X = b"".join(sorted(_f(A) for A in S))
    return hashlib.shake_256(KEY_DOMAIN + X).digest(32)


# ---------------------------------------------------------------------------
# Input decoding
# ---------------------------------------------------------------------------

def b85(x):
    if isinstance(x, str):
        x = x.encode()
    return base64.b85decode(x)


def load_output(path):
    raw = open(path, "rb").read().strip()

    try:
        raw = zlib.decompress(base64.b85decode(raw))
    except Exception:
        raw = zlib.decompress(base64.a85decode(raw))

    return json.loads(raw)


def decode_space(x):
    raw = b85(x)

    if len(raw) % 128:
        raise ValueError("bad encoded matrix-space size")

    return [
        [
            int.from_bytes(raw[o + 4 * r:o + 4 * r + 4], "little")
            for r in range(N)
        ]
        for o in range(0, len(raw), 128)
    ]


# ---------------------------------------------------------------------------
# Linear algebra on arbitrary bit vectors
# ---------------------------------------------------------------------------

def rref_basis(vs):
    piv = {}
    for x in vs:
        x = int(x)
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                for q in list(piv):
                    if (piv[q] >> p) & 1:
                        piv[q] ^= x
                piv[p] = x
                break
    return [piv[p] for p in sorted(piv, reverse=True)]


def nullspace(rows, ncols):
    rows = [int(x) for x in rows if x]
    rr = []
    pivots = []
    r = 0

    for c in range(ncols):
        q = next((q for q in range(r, len(rows))
                  if (rows[q] >> c) & 1), None)
        if q is None:
            continue

        rows[r], rows[q] = rows[q], rows[r]

        for q in range(len(rows)):
            if q != r and ((rows[q] >> c) & 1):
                rows[q] ^= rows[r]

        rr.append(rows[r])
        pivots.append(c)
        r += 1

        if r == len(rows):
            break

    pivot_set = set(pivots)
    out = []

    for free in range(ncols):
        if free in pivot_set:
            continue

        x = 1 << free

        for row, p in reversed(list(zip(rr, pivots))):
            if (row & x).bit_count() & 1:
                x ^= 1 << p

        out.append(x)

    return out


# ---------------------------------------------------------------------------
# Cheap conjugacy invariants
# ---------------------------------------------------------------------------

def full_rank_hist(space):
    """
    Compute rank histogram over ALL 2^m - 1 non-zero linear combinations.
    This is a complete invariant for the subspace: if two spaces span the
    same subspace (up to basis change), their full histograms match.
    """
    m = len(space)
    h = {}

    for mask in range(1, 1 << m):
        A = [0] * N
        for i in range(m):
            if (mask >> i) & 1:
                A = [x ^ y for x, y in zip(A, space[i])]
        r = rank(A)
        h[r] = h.get(r, 0) + 1

    return tuple(sorted(h.items()))


def invariant(space):
    return (
        len(space),
        full_rank_hist(space),
    )


# ---------------------------------------------------------------------------
# Recover an intertwiner.
#
# For aligned generators C_i,D_i:
#
#       S C_i = D_i S
#
# gives a homogeneous linear system in the N^2 entries of S.
# ---------------------------------------------------------------------------

def intertwiner_equations(C, D):
    rows = []

    for A, B in zip(C, D):
        # Equation for every (r,c):
        #
        # sum_k S[r,k] A[k,c] + sum_k B[r,k] S[k,c] = 0
        #
        for r in range(N):
            brow = B[r]

            for c in range(N):
                eq = 0

                for k in range(N):
                    if (A[k] >> c) & 1:
                        eq ^= 1 << (r * N + k)

                x = brow
                while x:
                    lb = x & -x
                    k = lb.bit_length() - 1
                    eq ^= 1 << (k * N + c)
                    x ^= lb

                if eq:
                    rows.append(eq)

    return rows


def solve_intertwiner(C, D):
    ns = nullspace(intertwiner_equations(C, D), N * N)

    if not ns:
        return None

    candidates = list(ns)

    # Usually the solution space is one-dimensional.  If not, sample
    # combinations until an invertible member is found.
    rng = random.Random(0x1337)

    for _ in range(4096):
        if candidates:
            if _ < len(candidates):
                x = candidates[_]
            else:
                x = 0
                for b in candidates:
                    if rng.getrandbits(1):
                        x ^= b

            if not x:
                continue

            S = unvec(x)
            if rank(S) == N:
                return S

    return None


def conjugate_space(S, C):
    Si = inverse(S)
    return [matmul(matmul(S, A), Si) for A in C]


def same_span(A, B):
    av = rref_basis(map(vec, A))
    bv = rref_basis(map(vec, B))
    return av == bv


def verify_conjugacy(S, C, D):
    try:
        return same_span(conjugate_space(S, C), D)
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# The published boxes are independently basis-randomised.  Recovering the
# basis correspondence is therefore necessary before solving S C_i=D_i S.
#
# We fingerprint individual generators using ranks of A, A+X and short
# products against the remaining generators.  Genuine conjugate spaces
# admit a unique compatible permutation in practice.
# ---------------------------------------------------------------------------

def generator_fp(space, i):
    A = space[i]
    vals = []

    for j, B in enumerate(space):
        if i == j:
            continue

        AB = matmul(A, B)
        BA = matmul(B, A)

        vals.append((
            rank([x ^ y for x, y in zip(A, B)]),
            rank(AB),
            rank(BA),
            rank([x ^ y for x, y in zip(AB, BA)]),
        ))

    vals.sort()
    return rank(A), tuple(vals)


def candidate_permutations(C, D):
    fc = [generator_fp(C, i) for i in range(len(C))]
    fd = [generator_fp(D, i) for i in range(len(D))]

    choices = []
    for f in fc:
        q = [j for j, g in enumerate(fd) if g == f]
        if not q:
            return
        choices.append(q)

    order = sorted(range(len(C)), key=lambda i: len(choices[i]))
    used = set()
    p = [-1] * len(C)

    def rec(k):
        if k == len(order):
            yield tuple(p)
            return

        i = order[k]

        for j in choices[i]:
            if j in used:
                continue
            p[i] = j
            used.add(j)
            yield from rec(k + 1)
            used.remove(j)
            p[i] = -1

    yield from rec(0)


def recover_direct(C, D):
    for p in candidate_permutations(C, D):
        DD = [D[p[i]] for i in range(len(C))]
        S = solve_intertwiner(C, DD)

        if S is not None and verify_conjugacy(S, C, D):
            return S

    return None


# ---------------------------------------------------------------------------
# Basis-independent fallback.
#
# Try short linear combinations as a new basis.  This handles the _o()
# random GL(m,2) basis change used by the challenge.
# ---------------------------------------------------------------------------

def combinations(space):
    m = len(space)
    out = []

    for mask in range(1, 1 << m):
        A = [0] * N
        for i in range(m):
            if (mask >> i) & 1:
                A = [x ^ y for x, y in zip(A, space[i])]
        out.append((mask, A))

    return out


def recover_with_basis_search(C, D):
    m = len(C)

    CC = combinations(C)
    DD = combinations(D)

    def elem_inv(A):
        return (rank(A), rank(matmul(A, A)))

    by_inv_c = {}
    by_inv_d = {}

    for mask, A in CC:
        by_inv_c.setdefault(elem_inv(A), []).append(A)

    for mask, A in DD:
        by_inv_d.setdefault(elem_inv(A), []).append(A)

    common = sorted(
        set(by_inv_c) & set(by_inv_d),
        key=lambda k: (len(by_inv_c[k]), len(by_inv_d[k])),
    )

    # Phase 1: find unique-matching groups (exactly 1 on each side)
    base_c, base_d = [], []

    for inv in common:
        if len(by_inv_c[inv]) == 1 and len(by_inv_d[inv]) == 1:
            base_c.append(by_inv_c[inv][0])
            base_d.append(by_inv_d[inv][0])

    if base_c:
        print(f"      Found {len(base_c)} unique-matching elements")
        S = solve_intertwiner(base_c, base_d)
        if S is not None and verify_conjugacy(S, C, D):
            return S
        if S is not None:
            print(f"      solve_intertwiner succeeded but verify failed")

    # Phase 2: small groups (<=6 elements each side)
    small = [inv for inv in common
             if 2 <= len(by_inv_c[inv]) == len(by_inv_d[inv]) <= 6
             and inv not in {elem_inv(b) for b in base_c}]

    print(f"      Small groups: {len(small)}")

    for inv in small:
        els_c = by_inv_c[inv]
        els_d = by_inv_d[inv]
        k = len(els_c)
        print(f"      Trying group inv={inv} with {k} elements")

        for perm in itertools.permutations(range(k)):
            tc = base_c + [els_c[i] for i in range(k)]
            td = base_d + [els_d[perm[i]] for i in range(k)]
            S = solve_intertwiner(tc, td)
            if S is not None and verify_conjugacy(S, C, D):
                return S

        base_c.extend(els_c)
        base_d.extend(els_d)

    # Phase 3: for remaining groups, try each C-element against each D-element
    # individually, using the current base to constrain S.
    for inv in common:
        if len(by_inv_c[inv]) > 6 or len(by_inv_d[inv]) > 6:
            continue
        if inv in {elem_inv(b) for b in base_c}:
            continue

        for A in by_inv_c[inv]:
            for B in by_inv_d[inv]:
                S = solve_intertwiner(base_c + [A], base_d + [B])
                if S is not None and verify_conjugacy(S, C, D):
                    return S

    return None


def recover_pair(C, D):
    # _o() may transpose a whole space.
    variants = [
        (C, D, False, False),
        ([transpose(A) for A in C], D, True, False),
        (C, [transpose(A) for A in D], False, True),
        (
            [transpose(A) for A in C],
            [transpose(A) for A in D],
            True,
            True,
        ),
    ]

    for X, Y, tc, td in variants:
        S = recover_direct(X, Y)
        if S is not None:
            print(f"      recover_direct succeeded (tc={tc}, td={td})")
        else:
            print(f"      recover_direct failed (tc={tc}, td={td})")

        if S is None:
            S = recover_with_basis_search(X, Y)
            if S is not None:
                print(f"      recover_with_basis_search succeeded (tc={tc}, td={td})")
            else:
                print(f"      recover_with_basis_search failed (tc={tc}, td={td})")

        if S is None:
            continue

        # _f() explicitly identifies S with inverse/transpose variants, so
        # returning the recovered representative is sufficient.
        if tc ^ td:
            try:
                S = transpose(inverse(S))
            except ValueError:
                continue

        return S

    return None


# ---------------------------------------------------------------------------
# Find the five genuine boxes and decrypt
# ---------------------------------------------------------------------------

def decrypt_blob(ct_field, key):
    blob = b85(ct_field)

    # Challenge output normally stores nonce || ciphertext || tag.
    candidates = []

    if len(blob) >= 12 + 16:
        candidates.append((blob[:12], blob[12:]))

    # Also accept JSON encodings where nonce and ciphertext are separate.
    for nonce, ct in candidates:
        try:
            return ChaCha20Poly1305(key).decrypt(nonce, ct, AAD)
        except Exception:
            pass

    return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "output.txt"
    obj = load_output(path)

    if obj.get("v") != 2:
        raise RuntimeError("unsupported Linchan version")

    boxes = []

    for i, box in enumerate(obj["boxes"]):
        boxes.append({
            "id": i,
            "m": int(box["m"]),
            "space": decode_space(box["x"]),
        })

    groups = {}

    for box in boxes:
        groups.setdefault(box["m"], []).append(box)

    secrets = []

    # There are 2 real pairs for m=16, 2 for m=17 and 1 for m=18.
    required = {16: 2, 17: 2, 18: 1}

    for m, want in required.items():
        G = groups.get(m, [])

        # First use inexpensive conjugacy invariants to eliminate almost all
        # decoy pairs.
        buckets = {}

        for box in G:
            inv = invariant(box["space"])
            buckets.setdefault(inv, []).append(box)

        candidate_pairs = []

        bucket_sizes = [len(b) for b in buckets.values()]
        print(f"  m={m}: {len(G)} boxes, {len(buckets)} buckets, sizes: {sorted(bucket_sizes, reverse=True)[:20]}")

        for bucket in buckets.values():
            if len(bucket) < 2:
                continue
            candidate_pairs.extend(itertools.combinations(bucket, 2))

        print(f"  m={m}: {len(candidate_pairs)} candidate pairs")

        found = 0
        used = set()

        for a, b in candidate_pairs:
            if found >= want:
                break

            if a["id"] in used or b["id"] in used:
                continue

            print(f"  Trying pair ({a['id']}, {b['id']})")
            S = recover_pair(a["space"], b["space"])

            if S is None:
                print(f"    recover_pair failed")
                continue

            secrets.append(S)
            used.add(a["id"])
            used.add(b["id"])
            found += 1

        if found != want:
            raise RuntimeError(
                f"failed to recover all m={m} pairs: {found}/{want}"
            )

    if len(secrets) != 5:
        raise RuntimeError(
            f"expected 5 secret matrices, recovered {len(secrets)}"
        )

    key = _k(secrets)
    pt = decrypt_blob(obj["ct"], key)

    if pt is None:
        raise RuntimeError("ChaCha20-Poly1305 authentication failed")

    try:
        print(pt.decode())
    except UnicodeDecodeError:
        sys.stdout.buffer.write(pt)


if __name__ == "__main__":
    main()