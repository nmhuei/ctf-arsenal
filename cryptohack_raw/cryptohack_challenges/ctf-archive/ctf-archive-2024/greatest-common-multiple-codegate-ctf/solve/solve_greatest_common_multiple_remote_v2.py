#!/usr/bin/env python3
import argparse
import ast
import hashlib
import itertools
import multiprocessing as mp
import os
import re
import socket
import string
import sys
import time

R = 0xE1000000000000000000000000000000
MASK = (1 << 128) - 1
ID = 1 << 127  # multiplicative identity for the bit order used by GHASH
START = 128
NCOLS = 128 + 128 * 127 // 2
LOW32 = (1 << 32) - 1

PAIR_LIST = []
for _i in range(128):
    for _j in range(_i + 1, 128):
        PAIR_LIST.append((_i, _j))


def gf_mul(x: int, y: int) -> int:
    z, v = 0, y
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= v
        v = ((v >> 1) ^ R) if (v & 1) else (v >> 1)
    return z & MASK


def gf_pow(x: int, e: int) -> int:
    r = ID
    while e:
        if e & 1:
            r = gf_mul(r, x)
        x = gf_mul(x, x)
        e >>= 1
    return r


def gf_inv(x: int) -> int:
    return gf_pow(x, (1 << 128) - 2)


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def quad_row(x: int) -> int:
    # row for quadratic monomials: linear part + x_i*x_j part.
    pos, y = [], x
    while y:
        lsb = y & -y
        pos.append(lsb.bit_length() - 1)
        y ^= lsb
    row = x
    for a, i in enumerate(pos):
        base = i * (255 - i) // 2
        for j in pos[a + 1:]:
            row ^= 1 << (START + base + (j - i - 1))
    return row


def echelon_basis(rows):
    basis = {}
    for row in rows:
        x = row
        while x:
            p = x.bit_length() - 1
            b = basis.get(p)
            if b is None:
                basis[p] = x
                break
            x ^= b
    return basis


def add_echelon(basis, x: int) -> bool:
    while x:
        p = x.bit_length() - 1
        b = basis.get(p)
        if b is None:
            basis[p] = x
            return True
        x ^= b
    return False


def nullvec_from_free(f: int, basis, pivots_asc=None) -> int:
    if pivots_asc is None:
        pivots_asc = sorted(basis)
    v = 1 << f
    for p in pivots_asc:
        if (basis[p] & v).bit_count() & 1:
            v ^= 1 << p
    return v


def polar_grad(q: int, d: int) -> int:
    g = 0
    pairs = q >> START
    while pairs:
        lsb = pairs & -pairs
        k = lsb.bit_length() - 1
        i, j = PAIR_LIST[k]
        if (d >> i) & 1:
            g ^= 1 << j
        if (d >> j) & 1:
            g ^= 1 << i
        pairs ^= lsb
    return g


def recover_perp_for_sample(d: int, quad_basis) -> list[int]:
    piv = set(quad_basis)
    pivots_asc = sorted(quad_basis)
    gb = {}
    for f in range(NCOLS):
        if f in piv:
            continue
        q = nullvec_from_free(f, quad_basis, pivots_asc)
        g = polar_grad(q, d)
        if g:
            add_echelon(gb, g)
            if len(gb) == 32:
                break
    if len(gb) != 32:
        raise RuntimeError("could not recover a 32-dimensional orthogonal space")
    return list(gb.values())


def in_subspace(perp, x: int) -> bool:
    return all(dot(f, x) == 0 for f in perp)


def solve_h_map(U_samples, W_perp) -> int:
    # Find nonzero h such that multiplication by h maps one 96D subspace to the other.
    rows = []
    for u in U_samples[:16]:
        cols = [gf_mul(u, 1 << j) for j in range(128)]
        for w in W_perp:
            r = 0
            for j, c in enumerate(cols):
                if dot(w, c):
                    r ^= 1 << j
            rows.append(r)
        basis = echelon_basis(rows)
        if 128 - len(basis) == 1:
            piv = set(basis)
            pivots_asc = sorted(basis)
            for f in range(128):
                if f not in piv:
                    return nullvec_from_free(f, basis, pivots_asc)
    raise RuntimeError("H linear map was not unique; collect more samples/retry")


def recover_H_from_u1_tags(tag_hexes: list[str]) -> int:
    diffs = [int(tag_hexes[i], 16) ^ int(tag_hexes[i - 1], 16) for i in range(1, len(tag_hexes))]
    diffs = [x for x in diffs if x]
    print(f"[+] u1 diffs: {len(diffs)}", file=sys.stderr)

    t0 = time.time()
    qb = echelon_basis(quad_row(x) for x in diffs)
    print(f"[+] quadratic rank = {len(qb)} in {time.time() - t0:.2f}s", file=sys.stderr)
    if len(qb) != 7232:
        raise RuntimeError(f"quadratic rank is {len(qb)}, expected 7232; increase --u1-samples")

    perp0 = recover_perp_for_sample(diffs[0], qb)
    other = next((x for x in diffs if not in_subspace(perp0, x)), None)
    if other is None:
        raise RuntimeError("all samples landed in one subspace; retry")
    perp1 = recover_perp_for_sample(other, qb)

    G0 = [x for x in diffs if in_subspace(perp0, x)]
    G1 = [x for x in diffs if not in_subspace(perp0, x)]
    cand = solve_h_map(G0, perp1)

    def valid(h: int, swap: bool = False) -> bool:
        h2 = gf_mul(h, h)
        h3 = gf_mul(h2, h)
        ih2, ih3 = gf_inv(h2), gf_inv(h3)
        A, B = (G1[:30], G0[:30]) if swap else (G0[:30], G1[:30])
        return all((gf_mul(x, ih2) & LOW32) == 0 for x in A) and all((gf_mul(x, ih3) & LOW32) == 0 for x in B)

    for h in (cand, gf_inv(cand)):
        if valid(h, False) or valid(h, True):
            print(f"[+] H = {h:032x}", file=sys.stderr)
            return h
    raise RuntimeError("could not orient H; retry")


class EquationBuilder:
    def __init__(self, H: int, m_ops: int):
        self.H = H
        self.nvars = 128 + 96 * (2 + m_ops)
        self.cache = {}
        max_chunks = 2 + m_ops
        max_blocks = 2 * ((12 * max_chunks + 15) // 16) + 8
        self.Hpow = [0] * (max_blocks + 1)
        self.Hpow[0] = ID
        for i in range(1, len(self.Hpow)):
            self.Hpow[i] = gf_mul(self.Hpow[i - 1], H)

    def get_mask(self, side: str, a: int, c: int, p: int) -> list[int]:
        key = (side, a, c, p)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        lenA, lenC = 12 * a, 12 * c
        nA = (lenA + 15) // 16
        nC = (lenC + 15) // 16
        data_blocks = nA + nC
        rows = [0] * 128
        for byte_j in range(12):
            glob = p * 12 + byte_j
            blk, q = divmod(glob, 16)
            power = (data_blocks + 1 - blk) if side == "A" else (nC + 1 - blk)
            hp = self.Hpow[power]
            for b in range(8):
                bitpos = 8 * (11 - byte_j) + (7 - b)
                block_bit = 8 * (15 - q) + (7 - b)
                coeff = gf_mul(1 << block_bit, hp)
                y = coeff
                while y:
                    lsb = y & -y
                    rows[lsb.bit_length() - 1] ^= 1 << bitpos
                    y ^= lsb
        self.cache[key] = rows
        return rows

    def obs_rows(self, A_ids: list[int], C_ids: list[int], tag_hex: str) -> list[int]:
        a, c = len(A_ids), len(C_ids)
        T = int(tag_hex, 16)
        rhs = T ^ gf_mul(((96 * a) << 64) | (96 * c), self.H)
        rows = [(1 << k) | (((rhs >> k) & 1) << self.nvars) for k in range(128)]
        for p, cid in enumerate(A_ids):
            masks = self.get_mask("A", a, c, p)
            sh = 128 + 96 * cid
            for k in range(128):
                rows[k] ^= masks[k] << sh
        for p, cid in enumerate(C_ids):
            masks = self.get_mask("C", a, c, p)
            sh = 128 + 96 * cid
            for k in range(128):
                rows[k] ^= masks[k] << sh
        return rows


def add_rows_to_basis(basis: dict[int, int], rows: list[int], nvars: int) -> bool:
    rhs_mask = 1 << nvars
    varmask = rhs_mask - 1
    for row in rows:
        x = row
        while True:
            coeff = x & varmask
            if coeff == 0:
                if x & rhs_mask:
                    return False
                break
            p = coeff.bit_length() - 1
            b = basis.get(p)
            if b is None:
                basis[p] = x
                break
            x ^= b
    return True


def solve_S_unique_from_basis(basis: dict[int, int], nvars: int):
    rhs_mask = 1 << nvars
    varmask = rhs_mask - 1
    pivots = sorted(basis)
    sol = 0
    for p in pivots:
        row = basis[p]
        rhs = 1 if (row & rhs_mask) else 0
        coeff = (row & varmask) ^ (1 << p)
        if rhs ^ ((coeff & sol).bit_count() & 1):
            sol ^= 1 << p

    pivset = set(basis)
    for f in range(nvars):
        if f in pivset:
            continue
        v = 1 << f
        for p in pivots:
            if (basis[p] & v).bit_count() & 1:
                v ^= 1 << p
        if v & MASK:
            return sol & MASK, False, len(basis)
    return sol & MASK, True, len(basis)


def recover_empty_tag(H: int, tags: list[str], ops: list[str]) -> int:
    bld = EquationBuilder(H, len(ops))
    init = {"bits": 0, "A": [0], "C": [1], "nid": 2, "basis": {}}
    if not add_rows_to_basis(init["basis"], bld.obs_rows(init["A"], init["C"], tags[0]), bld.nvars):
        raise RuntimeError("initial equations inconsistent")
    cands = [init]
    print(f"[+] solving {len(ops)} branch bits", file=sys.stderr)

    for i, op in enumerate(ops):
        new_cands = []
        for cand in cands:
            for target in (0, 1):  # 0 -> C / s[1], 1 -> A / s[0]
                A = list(cand["A"])
                C = list(cand["C"])
                nid = cand["nid"]
                basis = cand["basis"].copy()
                if op == "u2":
                    (A if target else C).append(nid)
                elif op == "u1":
                    if target:
                        A = [nid]
                    else:
                        C = [nid]
                else:
                    raise ValueError(op)
                if add_rows_to_basis(basis, bld.obs_rows(A, C, tags[i + 1]), bld.nvars):
                    new_cands.append({
                        "bits": cand["bits"] | (target << i),
                        "A": A,
                        "C": C,
                        "nid": nid + 1,
                        "basis": basis,
                    })
        cands = new_cands
        if not cands:
            raise RuntimeError(f"no branch candidates after step {i + 1}; retry")
        if len(cands) > 20000:
            raise RuntimeError(f"too many branch candidates ({len(cands)}); reduce --u2-samples or retry")
        if (i + 1) % 5 == 0 or len(cands) == 1:
            print(f"    step {i + 1:02d}: candidates={len(cands)}", file=sys.stderr)

    answers = []
    for cand in cands:
        S, unique, rank = solve_S_unique_from_basis(cand["basis"], bld.nvars)
        answers.append((S, unique, rank, cand["bits"]))

    unique_answers = sorted({S for S, unique, _, _ in answers if unique})
    if len(unique_answers) == 1:
        S = unique_answers[0]
        print(f"[+] empty tag = {S:032x}", file=sys.stderr)
        return S

    info = ", ".join(f"rank={rank}, unique={unique}" for _, unique, rank, _ in answers[:5])
    raise RuntimeError(f"empty tag not uniquely determined ({len(answers)} candidates; {info}); retry or increase --u2-samples")


class Tube:
    def __init__(self, host: str, port: int, timeout: float = 20.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass

    def sendline(self, s: str | bytes = b""):
        if isinstance(s, str):
            s = s.encode()
        self.sock.sendall(s + b"\n")

    def sendlines(self, lines: list[str]):
        self.sock.sendall(("\n".join(lines) + "\n").encode())

    def _recv_more(self):
        data = self.sock.recv(65536)
        if not data:
            raise EOFError("connection closed")
        self.buf += data
        return data

    def recv_until(self, token: bytes) -> bytes:
        while token not in self.buf:
            self._recv_more()
        idx = self.buf.index(token) + len(token)
        out, self.buf = self.buf[:idx], self.buf[idx:]
        return out

    def recv_regex(self, pat: bytes):
        rgx = re.compile(pat, re.S)
        while True:
            m = rgx.search(self.buf)
            if m:
                out = self.buf[:m.end()]
                self.buf = self.buf[m.end():]
                return m, out
            self._recv_more()

    def recv_all_available(self, delay=0.2) -> bytes:
        old_timeout = self.sock.gettimeout()
        self.sock.settimeout(delay)
        try:
            while True:
                try:
                    data = self.sock.recv(65536)
                    if not data:
                        break
                    self.buf += data
                except socket.timeout:
                    break
        finally:
            self.sock.settimeout(old_timeout)
        out, self.buf = self.buf, b""
        return out


def leading_zero_bits(digest: bytes) -> int:
    n = 0
    for b in digest:
        if b == 0:
            n += 8
        else:
            return n + (8 - b.bit_length())
    return n


def _pow_worker(args):
    prefix, bits, start, step, stop = args
    pref = prefix.encode()
    i = start
    while not stop.is_set():
        s = str(i).encode()
        if leading_zero_bits(hashlib.sha256(pref + s).digest()) >= bits:
            stop.set()
            return s.decode()
        i += step
    return None




def _md5_decimal_chunk(args):
    suffix, target_hex, start, stop = args
    target = target_hex.lower()
    for n in range(start, stop):
        if hashlib.md5(str(n).encode() + suffix).hexdigest() == target:
            return n
    return None


def solve_md5_decimal_pow(suffix: bytes, digest_hex: str, upper: int = 1 << 26, workers: int | None = None) -> str:
    workers = workers or max(1, min(os.cpu_count() or 1, 8))
    # Large chunks keep multiprocessing overhead low; 2**26 / 2**18 = 256 jobs.
    chunk = 1 << 18
    jobs = [(suffix, digest_hex, start, min(start + chunk, upper)) for start in range(0, upper, chunk)]
    if workers == 1:
        for job in jobs:
            ans = _md5_decimal_chunk(job)
            if ans is not None:
                return str(ans)
    else:
        with mp.Pool(workers) as pool:
            for ans in pool.imap_unordered(_md5_decimal_chunk, jobs, chunksize=1):
                if ans is not None:
                    pool.terminate()
                    pool.join()
                    return str(ans)
    raise RuntimeError("could not solve md5 decimal PoW")

def solve_hashcash(prefix: str, bits: int, workers: int | None = None) -> str:
    workers = workers or max(1, min(os.cpu_count() or 1, 8))
    if workers == 1:
        i = 0
        pref = prefix.encode()
        while True:
            s = str(i).encode()
            if leading_zero_bits(hashlib.sha256(pref + s).digest()) >= bits:
                return s.decode()
            i += 1
    mgr = mp.Manager()
    stop = mgr.Event()
    with mp.Pool(workers) as pool:
        for ans in pool.imap_unordered(_pow_worker, [(prefix, bits, i, workers, stop) for i in range(workers)]):
            if ans is not None:
                stop.set()
                return ans
    raise RuntimeError("PoW failed")


def brute_digest_unknown(known: str, digest_hex: str, unknown_first=True, max_len=5) -> str | None:
    chars = string.ascii_letters + string.digits
    target = digest_hex.lower()
    for ln in range(1, max_len + 1):
        for tup in itertools.product(chars, repeat=ln):
            x = "".join(tup)
            msg = (x + known) if unknown_first else (known + x)
            if hashlib.sha256(msg.encode()).hexdigest() == target:
                return x
    return None


def maybe_solve_pow(tube: Tube):
    # Read until either normal prompt appears or enough PoW text appears.
    if not tube.buf:
        tube._recv_more()
    time.sleep(0.1)
    banner = tube.recv_all_available(0.3)
    if b"> " in banner:
        tube.buf = banner
        return

    text = banner.decode(errors="ignore")
    if text:
        print(text, end="", file=sys.stderr)

    # CryptoHack archive PoW used by this service:
    # md5(str(n).encode() + b'...').hexdigest() = <digest>
    # Input n within range(2**26).
    m = re.search(
        r"md5\s*\(\s*str\(n\)\.encode\(\)\s*\+\s*(b(['\"]).*?\2)\s*\)\.hexdigest\(\)\s*=\s*([0-9a-fA-F]{32})",
        text,
        re.S,
    )
    if m:
        suffix_literal, digest_hex = m.group(1), m.group(3)
        try:
            suffix = ast.literal_eval(suffix_literal)
        except Exception:
            # Fallback for simple alphanumeric suffixes.
            suffix = suffix_literal[2:].strip("'\"").encode()
        upper_m = re.search(r"range\(\s*2\s*\*\*\s*(\d+)\s*\)", text)
        upper = 1 << int(upper_m.group(1)) if upper_m else (1 << 26)
        print(f"[+] solving md5 decimal PoW over range({upper})", file=sys.stderr)
        ans = solve_md5_decimal_pow(suffix, digest_hex, upper=upper)
        print(f"[+] PoW n = {ans}", file=sys.stderr)
        tube.sendline(ans)
        tube.recv_until(b"> ")
        return

    # Pattern 1: sha256(XXXX + suffix) == digest
    m = re.search(r"sha256\s*\(\s*(?:XXXX|\?\?\?\?)\s*\+\s*['\"]?([^'\")\s]+)['\"]?\s*\)\s*==\s*([0-9a-fA-F]{64})", text)
    if m:
        suffix, digest_hex = m.group(1), m.group(2)
        print("[+] solving digest-equality PoW", file=sys.stderr)
        ans = brute_digest_unknown(suffix, digest_hex, True, max_len=4)
        if ans is None:
            raise RuntimeError("could not brute-force digest PoW")
        tube.sendline(ans)
        tube.recv_until(b"> ")
        return

    # Pattern 2: sha256(prefix + XXXX) == digest
    m = re.search(r"sha256\s*\(\s*['\"]?([^'\")\s]+)['\"]?\s*\+\s*(?:XXXX|\?\?\?\?)\s*\)\s*==\s*([0-9a-fA-F]{64})", text)
    if m:
        prefix, digest_hex = m.group(1), m.group(2)
        print("[+] solving digest-equality PoW", file=sys.stderr)
        ans = brute_digest_unknown(prefix, digest_hex, False, max_len=4)
        if ans is None:
            raise RuntimeError("could not brute-force digest PoW")
        tube.sendline(ans)
        tube.recv_until(b"> ")
        return

    # Pattern 3: hashcash-style: prefix + nonce has N leading zero bits.
    bits_match = re.search(r"(\d+)\s*(?:leading\s*)?(?:zero|0)\s*bits", text, re.I) or re.search(r"difficulty\D+(\d+)", text, re.I)
    prefix_match = (
        re.search(r"prefix\s*[:=]\s*['\"]?([0-9A-Za-z_./:+-]+)['\"]?", text, re.I)
        or re.search(r"starting with\s*['\"]?([0-9A-Za-z_./:+-]+)['\"]?", text, re.I)
        or re.search(r"sha256\s*\(\s*['\"]?([0-9A-Za-z_./:+-]+)['\"]?\s*\+", text, re.I)
    )
    if bits_match and prefix_match:
        bits = int(bits_match.group(1))
        prefix = prefix_match.group(1)
        print(f"[+] solving hashcash PoW: sha256({prefix!r}+x) has {bits} leading zero bits", file=sys.stderr)
        ans = solve_hashcash(prefix, bits)
        tube.sendline(ans)
        tube.recv_until(b"> ")
        return

    raise RuntimeError("unrecognized PoW prompt; run once and paste the prompt so I can add its parser")


def recv_n_tags(tube: Tube, n: int) -> list[str]:
    tags = []
    pat = re.compile(rb"tag:\s*([0-9a-fA-F]{32})")
    while len(tags) < n:
        m = pat.search(tube.buf)
        if m:
            tags.append(m.group(1).decode().lower())
            tube.buf = tube.buf[m.end():]
        else:
            tube._recv_more()
    return tags


def run_remote(host: str, port: int, u1_samples: int, u2_samples: int):
    tube = Tube(host, port)
    try:
        maybe_solve_pow(tube)
        print(f"[+] connected; collecting {u1_samples + 1} u1-stage tags and {u2_samples} u2-stage tags", file=sys.stderr)

        cmds = ["tag"]
        for _ in range(u1_samples):
            cmds += ["u1", "tag"]
        for _ in range(u2_samples):
            cmds += ["u2", "tag"]
        cmds.append("")  # leave the command loop; server will ask for the final empty-message tag
        tube.sendlines(cmds)

        all_tags = recv_n_tags(tube, u1_samples + 1 + u2_samples)
        u1_tags = all_tags[:u1_samples + 1]
        s_tags = [u1_tags[-1]] + all_tags[u1_samples + 1:]

        t0 = time.time()
        H = recover_H_from_u1_tags(u1_tags)
        S = recover_empty_tag(H, s_tags, ["u2"] * u2_samples)
        print(f"[+] compute time: {time.time() - t0:.2f}s", file=sys.stderr)

        # Final prompt is exactly "tag: ". It may already be buffered.
        if b"tag:" not in tube.buf:
            tube.recv_until(b"tag: ")
        else:
            tube.recv_until(b"tag:")
        tube.sendline(f"{S:032x}")
        print(tube.recv_all_available(2.0).decode(errors="replace"))
    finally:
        tube.close()


def main():
    ap = argparse.ArgumentParser(description="Exploit for CryptoHack/CODEGATE Greatest Common Multiple")
    ap.add_argument("host", nargs="?", default="archive.cryptohack.org")
    ap.add_argument("port", nargs="?", type=int, default=2762)
    ap.add_argument("--u1-samples", type=int, default=7250, help="u1 updates used to recover H; increase if rank != 7232")
    ap.add_argument("--u2-samples", type=int, default=30, help="u2 updates used to recover the empty tag; increase/retry if not unique")
    args = ap.parse_args()
    run_remote(args.host, args.port, args.u1_samples, args.u2_samples)


if __name__ == "__main__":
    main()
