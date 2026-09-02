#!/usr/bin/env python3
import socket
import sys
import random
import time

N = 128
K_SUBSPACE = 14
N_RANDOM = 2200
XS_FOR_RANK = 768
SEED = 0x0ec5c2024
HEXCHARS = set(b"0123456789abcdefABCDEF")

# ---------- GF(2) linear algebra on 128-bit integers ----------
def rank_basis(vs, stop=None):
    basis = {}
    for v in vs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                if stop is not None and len(basis) >= stop:
                    return len(basis), list(basis.values())
                break
    return len(basis), list(basis.values())

def rref_rows(rows, n=N):
    rows = [x for x in rows if x]
    r = 0
    pivots = []
    for col in range(n - 1, -1, -1):
        pivot = None
        for i in range(r, len(rows)):
            if (rows[i] >> col) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and ((rows[i] >> col) & 1):
                rows[i] ^= rows[r]
        pivots.append(col)
        r += 1
        if r == len(rows):
            break
    return rows[:r], pivots

def nullspace_rows(rows, n=N):
    rr, pivots = rref_rows(rows, n)
    pivot_set = set(pivots)
    out = []
    for f in range(n):
        if f in pivot_set:
            continue
        v = 1 << f
        for row, p in zip(rr, pivots):
            if (row >> f) & 1:
                v |= 1 << p
        out.append(v)
    return out

def canonical(rows):
    return tuple(rref_rows(rows, N)[0])

def eval_rows(rows, x):
    y = 0
    for i, row in enumerate(rows):
        if (row & x).bit_count() & 1:
            y |= 1 << i
    return y

def invert_row_matrix(rows, n=N):
    mat = [[rows[i], 1 << i] for i in range(n)]
    r = 0
    for col in range(n - 1, -1, -1):
        pivot = None
        for i in range(r, n):
            if (mat[i][0] >> col) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        for i in range(n):
            if i != r and ((mat[i][0] >> col) & 1):
                mat[i][0] ^= mat[r][0]
                mat[i][1] ^= mat[r][1]
        r += 1
    if r != n:
        raise RuntimeError(f"input coordinate matrix is not invertible, rank={r}")
    pairs = [(mat[i][0].bit_length() - 1, mat[i][1]) for i in range(n)]
    def solve(y):
        x = 0
        for col, comb in pairs:
            if (comb & y).bit_count() & 1:
                x |= 1 << col
        return x
    return solve

# ---------- query generation ----------
def independent_vectors(rng, k):
    basis = []
    rb = {}
    while len(basis) < k:
        v = rng.getrandbits(128)
        x = v
        while x:
            p = x.bit_length() - 1
            if p in rb:
                x ^= rb[p]
            else:
                rb[p] = x
                basis.append(v)
                break
    return basis

def make_queries():
    rng = random.Random(SEED)
    basis = independent_vectors(rng, K_SUBSPACE)
    U = [0]
    for b in basis:
        U += [p ^ b for p in U]

    seen = set(U)
    rnd = []
    while len(rnd) < N_RANDOM:
        v = rng.getrandbits(128)
        if v not in seen:
            rnd.append(v)
            seen.add(v)
    Q = U + rnd
    return rng, U, rnd, Q

# ---------- cryptanalysis ----------
def recover_decryptor(U, rnd, Q, outs, verbose=True):
    rng = random.Random(SEED ^ 0xBAD5EED)
    if verbose:
        print(f"[+] recovering from {len(Q)} chosen blocks")

    # 1) Recover the 16 output byte hyperplanes M_i from derivatives inside U.
    xs = U[:]
    rng.shuffle(xs)
    xs = xs[:XS_FOR_RANK]
    cands = U[1:]
    rng.shuffle(cands)

    clusters = {}
    examples = {}
    processed = 0
    for d in cands:
        processed += 1
        vecs = (outs[x] ^ outs[x ^ d] for x in xs)
        r, b = rank_basis(vecs)
        if r == 120:
            eqs = nullspace_rows(b)
            can = canonical(eqs)
            clusters[can] = clusters.get(can, 0) + 1
            examples[can] = eqs
            if len(clusters) == 16:
                break
    if len(clusters) != 16:
        # Second pass with all U points if unlucky.
        clusters.clear()
        examples.clear()
        for d in cands:
            vecs = (outs[x] ^ outs[x ^ d] for x in U)
            r, b = rank_basis(vecs)
            if r == 120:
                eqs = nullspace_rows(b)
                can = canonical(eqs)
                clusters[can] = clusters.get(can, 0) + 1
                examples[can] = eqs
                if len(clusters) == 16:
                    break
    if len(clusters) != 16:
        raise RuntimeError(f"could not recover all output byte spaces, got {len(clusters)}")
    M_eqs = list(examples.values())
    if verbose:
        print(f"[+] recovered 16 output byte quotients after {processed} candidates")

    # 2) For each output quotient P_i, q_i(d)=P_i(E(0)^E(d)) is an unknown
    #    permutation of the hidden input byte. Equal q_i values give differences
    #    in the kernel H_i. Collisions recover each 120-dimensional H_i.
    E0 = outs[0]
    A_eqs = []
    for idx, eqs in enumerate(M_eqs):
        buckets = {}
        for x in rnd:
            q = eval_rows(eqs, E0 ^ outs[x])
            buckets.setdefault(q, []).append(x)
        diffs = []
        for arr in buckets.values():
            if len(arr) >= 2:
                base = arr[0]
                diffs.extend(base ^ v for v in arr[1:])
        r, b = rank_basis(diffs)
        if r < 120:
            raise RuntimeError(f"not enough collisions for input byte {idx}: rank={r}")
        rows = nullspace_rows(b)
        if len(rows) != 8:
            raise RuntimeError(f"bad input quotient dimension for byte {idx}: {len(rows)}")
        A_eqs.append(rows)
    A_rows = [row for rows in A_eqs for row in rows]
    arank, _ = rank_basis(A_rows)
    if arank != 128:
        raise RuntimeError(f"input coordinates are not full rank: {arank}")
    solve_A = invert_row_matrix(A_rows)
    if verbose:
        print("[+] recovered 16 input byte quotients")

    # 3) Learn the 16 equivalent 8-bit S-boxes from the already queried points.
    inv_tables = []
    for i in range(16):
        table = [None] * 256
        for x in Q:
            a = eval_rows(A_eqs[i], x)
            b = eval_rows(M_eqs[i], outs[x])
            if table[a] is not None and table[a] != b:
                raise RuntimeError(f"inconsistent table for byte {i}, input {a}")
            table[a] = b
        missing = [j for j, v in enumerate(table) if v is None]
        if missing:
            raise RuntimeError(f"missing {len(missing)} entries in table {i}")
        inv = [None] * 256
        for a, b in enumerate(table):
            if inv[b] is not None:
                raise RuntimeError(f"non-bijective equivalent table {i}")
            inv[b] = a
        inv_tables.append(inv)
    if verbose:
        print("[+] learned equivalent S-boxes; decryptor ready")

    def decrypt_block(c):
        y = 0
        for i in range(16):
            b = eval_rows(M_eqs[i], c)
            a = inv_tables[i][b]
            y |= a << (8 * i)
        return solve_A(y)
    return decrypt_block

# ---------- network helpers ----------
def recv_until(sock, marker=b"> ", timeout=300):
    sock.settimeout(timeout)
    data = bytearray()
    while not data.endswith(marker):
        chunk = sock.recv(65536)
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)

def recv_rest(sock, timeout=5):
    sock.settimeout(timeout)
    data = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        data.extend(chunk)
    return bytes(data)

def hex_lines(blob):
    out = []
    for line in blob.splitlines():
        s = line.strip()
        if s.startswith(b">"):
            s = s[1:].strip()
        if s and all(c in HEXCHARS for c in s):
            out.append(s.decode())
    return out

def solve_remote(host, port):
    rng, U, rnd, Q = make_queries()
    payload = b"".join(x.to_bytes(16, "big") for x in Q).hex().encode()
    print(f"[+] connecting to {host}:{port}")
    print(f"[+] sending {len(Q)} chosen plaintext blocks")

    with socket.create_connection((host, int(port)), timeout=30) as sock:
        recv_until(sock)  # initial prompt
        sock.sendall(payload + b"\n")

        first = recv_until(sock)  # oracle ciphertext, separator, first challenge, prompt
        hxs = hex_lines(first)
        if len(hxs) < 2:
            raise RuntimeError(f"could not parse initial response: {first[:200]!r}")
        oracle_hex = hxs[0]
        expected = (len(Q) + 1) * 32  # extra PKCS#7 padding block
        if len(oracle_hex) < len(Q) * 32:
            raise RuntimeError(f"oracle output too short: {len(oracle_hex)} hex chars")
        if len(oracle_hex) != expected:
            print(f"[!] oracle hex length {len(oracle_hex)} != expected {expected}; continuing")
        outs = {}
        for i, x in enumerate(Q):
            block_hex = oracle_hex[32 * i: 32 * (i + 1)]
            outs[x] = int(block_hex, 16)

        decrypt = recover_decryptor(U, rnd, Q, outs, verbose=True)

        challenge_hex = hxs[-1]
        for round_idx in range(100):
            c = int(challenge_hex, 16)
            p = decrypt(c).to_bytes(16, "big")
            if p[-1] != 1:
                print(f"[!] warning: bad padding in round {round_idx}: {p.hex()}")
            guess = p[:-1].hex().encode()
            sock.sendall(guess + b"\n")
            print(f"[+] round {round_idx:03d}: {guess.decode()}")
            if round_idx == 99:
                break
            resp = recv_until(sock)
            hxs = hex_lines(resp)
            if not hxs:
                raise RuntimeError(f"could not parse challenge after round {round_idx}: {resp[:200]!r}")
            challenge_hex = hxs[-1]

        tail = recv_rest(sock)
        print(tail.decode(errors="replace"))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} HOST PORT")
        print(f"Example: {sys.argv[0]} archive.cryptohack.org 62821")
        sys.exit(1)
    solve_remote(sys.argv[1], int(sys.argv[2]))
