#!/usr/bin/env sage
# Hyper512 (HITCON CTF) — Optimized solver
#
# Speedup summary vs. original:
#
#  1. Default method is the published fast-correlation style attack.
#     It uses all 32768 gift bits and avoids the slow Groebner system.
#
#  2. lin() uses set-bit iteration instead of full 128-step scan
#     → skips zero-bits, ~50% fewer loop iterations on average.
#
#  3. Equation loop inlined (no function call per bit)
#
#  4. Groebner algorithm: 'libsingular:slimgb' (faster than PolyBoRi default
#     on overdetermined systems with many equations).  Falls back to default
#     on error.
#
#  5. gen_masks uses deque to avoid O(128) list copy per clock.
#
#  Usage:
#    sage solve/solve_hyper512_fast.sage            # fast default (all gift bits)
#    sage solve/solve_hyper512_fast.sage --method groebner --nbits 4096
#    sage solve/solve_hyper512_fast.sage --check        # layout check only

from __future__ import print_function
from pathlib import Path
from hashlib import sha256
from binascii import unhexlify
from operator import xor as bitxor
from collections import deque
import argparse
import sys
import time
import random

MASKS = [
    0x6D6AC812F52A212D5A0B9F3117801FD5,
    0xD736F40E0DED96B603F62CBE394FEF3D,
    0xA55746EF3955B07595ABC13B9EBEED6B,
    0xD670201BAC7515352A273372B2A95B23,
]
CALLS = [3, 1, 4, 2]


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def script_dir():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd().resolve()


def find_challenge_root():
    candidates = []
    here = script_dir()
    cwd = Path.cwd().resolve()
    candidates += [here.parent, cwd, cwd.parent, here]
    seen = set(); uniq = []
    for p in candidates:
        if p not in seen:
            seen.add(p); uniq.append(p)
    for root in uniq:
        if (root / 'files').is_dir() and list((root / 'files').glob('output_*.txt')):
            return root
    raise FileNotFoundError(
        'Cannot find challenge root.\nScript dir: %s\nCwd: %s' % (here, cwd))


def find_output_file(root, explicit=None):
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if not p.exists():
            raise FileNotFoundError('Output file not found: %s' % p)
        return p
    outs = sorted((root / 'files').glob('output_*.txt'))
    if not outs:
        raise FileNotFoundError('No files/output_*.txt under %s' % root)
    return outs[0]


# ---------------------------------------------------------------------------
# Bit I/O
# ---------------------------------------------------------------------------

def bits_from_bytes(bs):
    for b in bs:
        for i in range(7, -1, -1):
            yield (b >> i) & 1


def bytes_from_bits(bits):
    out = bytearray()
    for i in range(0, len(bits), 8):
        v = 0
        for b in bits[i:i+8]:
            v = (v << 1) | int(b)
        out.append(v)
    return bytes(out)


# ---------------------------------------------------------------------------
# gen_masks — uses deque to avoid O(128) list copy per clock
# ---------------------------------------------------------------------------

def gen_masks(mask, calls, nbits):
    """
    Return list of nbits ints.  out[p] is a 128-bit mask: bit i set iff
    the p-th keystream bit depends linearly on initial state bit i.
    """
    st = deque(1 << i for i in range(128))
    taps = [i for i in range(128) if (mask >> i) & 1]
    out = []
    for _ in range(nbits):
        v = 0
        for __ in range(calls):
            v = bitxor(v, st[0])
            new = 0
            for j in taps:
                new = bitxor(new, st[j])
            st.popleft()
            st.append(new)
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# lin — build linear BPR polynomial from a bitmask
# Iterates only over SET bits (skips zeros) for ~2x speedup vs range(128)
# ---------------------------------------------------------------------------

def lin(packed_mask, ks_slice):
    """
    packed_mask: 128-bit int
    ks_slice: pre-sliced list of 128 BPR generators
    Returns: linear polynomial (sum of generators at set bit positions)
    """
    result = None
    m = packed_mask
    while m:
        lsb = m & (-m)
        i = lsb.bit_length() - 1
        g = ks_slice[i]
        result = g if result is None else (result + g)
        m = bitxor(m, lsb)
    return result   # None if packed_mask == 0


# ---------------------------------------------------------------------------
# Filter / LFSR (for verification only)
# ---------------------------------------------------------------------------

def fbit_plain(x, y, z, w):
    return sha256(str(3142 + 3*x + y + 4*z + 2*w).encode()).digest()[0] & 1


class LFSR:
    def __init__(self, n, key, mask):
        self.n = int(n)
        one = int(1)
        self.state = int(key) & ((one << self.n) - one)
        self.mask = int(mask)

    def __call__(self):
        one = int(1)
        b = int(self.state & one)
        fb = int((self.state & self.mask).bit_count() & one)
        self.state = int((self.state >> one) | (fb << (self.n - one)))
        return b


class Cipher:
    def __init__(self, key):
        key = int(key)
        self.l1 = LFSR(128, key, MASKS[0]); key >>= 128
        self.l2 = LFSR(128, key, MASKS[1]); key >>= 128
        self.l3 = LFSR(128, key, MASKS[2]); key >>= 128
        self.l4 = LFSR(128, key, MASKS[3])

    def bit(self):
        x = bitxor(bitxor(self.l1(), self.l1()), self.l1())
        y = self.l2()
        z = bitxor(bitxor(bitxor(self.l3(), self.l3()), self.l3()), self.l3())
        w = bitxor(self.l4(), self.l4())
        return fbit_plain(x, y, z, w)

    def stream(self):
        while True:
            v = 0
            for i in range(7, -1, -1):
                v |= self.bit() << i
            yield v


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_output(path):
    lines = [x.strip() for x in Path(path).read_text().splitlines() if x.strip()]
    if len(lines) < 2:
        raise ValueError('Output file must have gift hex and ct hex on two lines')
    return unhexlify(lines[0]), unhexlify(lines[1])


def z3_xor_many(items):
    import z3

    if not items:
        return z3.BoolVal(False)
    acc = items[0]
    for item in items[1:]:
        acc = z3.Xor(acc, item)
    return acc


def z3_lin(mask, ks_slice):
    terms = []
    m = int(mask)
    while m:
        lsb = m & (-m)
        terms.append(ks_slice[lsb.bit_length() - 1])
        m = bitxor(m, lsb)
    return z3_xor_many(terms)


def solve_with_z3(all_masks, known, timeout_ms=0):
    import z3

    s = z3.Solver()
    if timeout_ms:
        s.set(timeout=timeout_ms)

    ks = [z3.Bool('k%d' % i) for i in range(512)]
    ks0, ks1, ks2, ks3 = ks[0:128], ks[128:256], ks[256:384], ks[384:512]
    expr_cache = {}

    def cached_lin(register_id, pos, ks_slice):
        key = (register_id, all_masks[register_id][pos])
        expr = expr_cache.get(key)
        if expr is None:
            expr = z3_lin(key[1], ks_slice)
            expr_cache[key] = expr
        return expr

    # Truth-table encoding of the filter is smaller for Z3 than expanding ANF.
    allowed = {0: [], 1: []}
    for x in (False, True):
        for y in (False, True):
            for z in (False, True):
                for w in (False, True):
                    bit = fbit_plain(int(x), int(y), int(z), int(w))
                    allowed[bit].append((x, y, z, w))

    t0 = time.time()
    for pos, bit in enumerate(known):
        x = cached_lin(0, pos, ks0)
        y = cached_lin(1, pos, ks1)
        z = cached_lin(2, pos, ks2)
        w = cached_lin(3, pos, ks3)
        s.add(z3.Or(*[
            z3.And(x == a, y == b, z == c, w == d)
            for a, b, c, d in allowed[bit]
        ]))
        if pos and pos % 512 == 0:
            print('[+]   SAT constraints: %d/%d  t=%.1fs'
                  % (pos, len(known), time.time() - t0))

    print('[+]   cached linear expressions:', len(expr_cache))
    print('[+]   solving with Z3...')
    res = s.check()
    print('[+]   Z3 result:', res)
    if res != z3.sat:
        return None

    model = s.model()
    key = 0
    for i, v in enumerate(ks):
        if z3.is_true(model.eval(v, model_completion=True)):
            key |= 1 << i
    return key


def mask_to_cms_vars(mask, offset):
    out = []
    m = int(mask)
    offset = int(offset)
    while m:
        lsb = m & (-m)
        out.append(int(offset + lsb.bit_length()))
        m = bitxor(m, lsb)
    return out


def solve_with_cryptosat(all_masks, known):
    from pycryptosat import Solver

    solver = Solver()
    next_var = 513
    t0 = time.time()

    allowed = {0: [], 1: []}
    for x in (False, True):
        for y in (False, True):
            for z in (False, True):
                for w in (False, True):
                    bit = fbit_plain(int(x), int(y), int(z), int(w))
                    allowed[bit].append((x, y, z, w))

    for pos, bit in enumerate(known):
        outs = [int(next_var), int(next_var + 1), int(next_var + 2), int(next_var + 3)]
        next_var += 4
        for reg, out_var in enumerate(outs):
            clause = mask_to_cms_vars(all_masks[reg][pos], 128 * reg)
            if clause:
                solver.add_xor_clause(clause + [out_var], False)
            else:
                solver.add_clause([-out_var])

        # Forbid every input tuple that would produce the wrong output bit.
        for vals in allowed[1 - bit]:
            solver.add_clause([
                -var if val else var
                for var, val in zip(outs, vals)
            ])

        if pos and pos % 2048 == 0:
            print('[+]   CMS constraints: %d/%d  vars=%d  t=%.1fs'
                  % (pos, len(known), next_var - 1, time.time() - t0))

    print('[+]   CMS vars:', next_var - 1)
    print('[+]   solving with CryptoMiniSat...')
    sat, solution = solver.solve()
    print('[+]   CryptoMiniSat result:', sat)
    if not sat:
        return None

    key = 0
    for i in range(512):
        if solution[i + 1]:
            key |= 1 << i
    return key


PAIR_BASES = {
    (0, 1): 512,
    (0, 2): 512 + 128 * 128,
    (1, 2): 512 + 2 * 128 * 128,
    (1, 3): 512 + 3 * 128 * 128,
    (0, 3): 512 + 4 * 128 * 128,
    (2, 3): 512 + 5 * 128 * 128,
}
LIN_VARS = 512
TOTAL_LIN_VARS = 512 + 6 * 128 * 128
YZ_PRODUCT_VARS = 128 * 128
YZ_TOTAL_VARS = YZ_PRODUCT_VARS + 256


def toggle_linear(row, mask, offset):
    m = int(mask)
    offset = int(offset)
    while m:
        lsb = m & (-m)
        row = bitxor(row, 1 << (offset + lsb.bit_length() - 1))
        m = bitxor(m, lsb)
    return row


def toggle_product(row, a, b, pair):
    ma = int(a)
    mb_all = int(b)
    base = PAIR_BASES[pair]
    while ma:
        la = ma & (-ma)
        i = la.bit_length() - 1
        row = bitxor(row, mb_all << (base + 128 * i))
        ma = bitxor(ma, la)
    return row


def lin_row_for_bit(masks_at_pos, bit):
    x, y, z, w = masks_at_pos
    rows = []
    rhs_bit = 1 << TOTAL_LIN_VARS
    if bit == 0:
        row = 0
        row = toggle_product(row, x, y, (0, 1))
        row = toggle_linear(row, z, 256)
        row = toggle_product(row, x, z, (0, 2))
        row = toggle_product(row, y, z, (1, 2))
        rows.append(row)

        row = 0
        row = toggle_linear(row, y, 128)
        row = toggle_linear(row, z, 256)
        row = toggle_product(row, x, z, (0, 2))
        row = toggle_product(row, y, w, (1, 3))
        rows.append(row)

        row = 0
        row = toggle_product(row, x, z, (0, 2))
        row = toggle_product(row, z, w, (2, 3))
        rows.append(row)
    else:
        row = rhs_bit
        row = toggle_linear(row, y, 128)
        row = toggle_linear(row, z, 256)
        row = toggle_product(row, y, z, (1, 2))
        rows.append(row)

        row = rhs_bit
        row = toggle_linear(row, x, 0)
        row = toggle_linear(row, y, 128)
        row = toggle_product(row, x, y, (0, 1))
        row = toggle_linear(row, z, 256)
        row = toggle_product(row, x, z, (0, 2))
        row = toggle_product(row, x, w, (0, 3))
        row = toggle_product(row, y, w, (1, 3))
        rows.append(row)

        row = 0
        row = toggle_linear(row, w, 384)
        row = toggle_product(row, x, w, (0, 3))
        row = toggle_product(row, z, w, (2, 3))
        rows.append(row)
    return rows


def solve_linearized(all_masks, known):
    rhs_bit = 1 << TOTAL_LIN_VARS
    basis = {}
    t0 = time.time()
    equations = 0

    for pos, bit in enumerate(known):
        masks_at_pos = [all_masks[i][pos] for i in range(4)]
        for row in lin_row_for_bit(masks_at_pos, bit):
            equations += 1
            while row:
                p = row.bit_length() - 1
                if p == TOTAL_LIN_VARS:
                    p = bitxor(row, rhs_bit).bit_length() - 1
                    if p < 0:
                        break
                old = basis.get(p)
                if old is None:
                    basis[p] = row
                    break
                row = bitxor(row, old)
        if pos and pos % 1024 == 0:
            print('[+]   linear equations: %d/%d  rank=%d  t=%.1fs'
                  % (pos, len(known), len(basis), time.time() - t0))

    print('[+]   equations:', equations)
    print('[+]   rank:', len(basis), '/', TOTAL_LIN_VARS)

    # Convert to reduced form enough to detect fixed original key bits.
    pivots = sorted(basis)
    for p in reversed(pivots):
        row = basis[p]
        for q in [q for q in basis if q < p and ((basis[q] >> p) & 1)]:
            basis[q] = bitxor(basis[q], row)

    key = 0
    recovered = 0
    for i in range(512):
        row = basis.get(i)
        if row is None:
            continue
        if row & ~(rhs_bit | (1 << i)) == 0:
            recovered += 1
            if row & rhs_bit:
                key |= 1 << i

    print('[+]   fixed key bits:', recovered, '/ 512')
    if recovered != 512:
        return None
    return key


def gf2_add_row(basis, row, nvars):
    rhs_bit = 1 << nvars
    while row:
        if row == rhs_bit:
            return False
        p = row.bit_length() - 1
        if p == nvars:
            p = bitxor(row, rhs_bit).bit_length() - 1
            if p < 0:
                return False
        old = basis.get(p)
        if old is None:
            basis[p] = row
            return True
        row = bitxor(row, old)
    return True


def gf2_build_basis(rows, nvars):
    basis = {}
    for row in rows:
        if not gf2_add_row(basis, row, nvars):
            return None
    return basis


def gf2_solution_from_basis(basis, nvars):
    if len(basis) < nvars:
        return None

    sol = 0
    for p in range(nvars):
        row = basis.get(p)
        if row is None:
            return None
        known_part = int(row & ((1 << p) - 1))
        val = bitxor(((known_part & int(sol)).bit_count() & 1), int((row >> nvars) & 1))
        if val:
            sol |= 1 << p
    return sol


def gf2_solve_full(rows, nvars):
    basis = gf2_build_basis(rows, nvars)
    if basis is None:
        return None
    return gf2_solution_from_basis(basis, nvars)


def yz_product_row(y_mask, z_mask):
    row = 0
    my = int(y_mask)
    mz = int(z_mask)
    while my:
        ly = my & (-my)
        i = ly.bit_length() - 1
        row = bitxor(row, mz << (128 * i))
        my = bitxor(my, ly)
    return row


def yz_equation_row(y_mask, z_mask):
    row = 1 << YZ_TOTAL_VARS
    row = bitxor(row, yz_product_row(y_mask, z_mask))
    row = toggle_linear(row, y_mask, YZ_PRODUCT_VARS)
    row = toggle_linear(row, z_mask, YZ_PRODUCT_VARS + 128)
    return row


def yz_zero_guess_rows(var_id):
    rows = [1 << var_id]
    if var_id < 128:
        for j in range(128):
            rows.append(1 << (128 * var_id + j))
    else:
        j = var_id - 128
        for i in range(128):
            rows.append(1 << (128 * i + j))
    return rows


def parity_from_mask(state, mask):
    return (int(state & int(mask)).bit_count() & 1)


def solve_128_linear(equations):
    rows = []
    for mask, bit in equations:
        rows.append(int(mask) | (int(bit) << 128))
    sol = gf2_solve_full(rows, 128)
    return sol


def solve_fast_correlation(all_masks, known):
    print('[+]   building y/z equations from output=1 bits...')
    base_rows = []
    for pos, bit in enumerate(known):
        if bit == 1:
            base_rows.append(yz_equation_row(all_masks[1][pos], all_masks[2][pos]))
    print('[+]   y/z equations:', len(base_rows), 'unknowns:', YZ_TOTAL_VARS)
    t0 = time.time()
    base_basis = gf2_build_basis(base_rows, YZ_TOTAL_VARS)
    if base_basis is None:
        print('[!]   inconsistent base y/z system')
        return None
    print('[+]   base rank:', len(base_basis), 'built in %.1fs' % (time.time() - t0))

    rng = random.Random(int(0x4859504552353132))
    guess_triples = [tuple(rng.sample(range(256), 3)) for _ in range(4096)]
    tries = 0
    yz_sol = None
    for guessed in guess_triples:
        basis = dict(base_basis)
        ok_basis = True
        for var_id in guessed:
            for row in yz_zero_guess_rows(var_id):
                if not gf2_add_row(basis, row, YZ_TOTAL_VARS):
                    ok_basis = False
                    break
            if not ok_basis:
                break
        tries += 1
        if tries % 16 == 0:
            print('[+]   y/z guess tries:', tries)
        if not ok_basis:
            continue
        sol = gf2_solution_from_basis(basis, YZ_TOTAL_VARS)
        if sol is None:
            continue

        y_state = (sol >> YZ_PRODUCT_VARS) & ((1 << 128) - 1)
        z_state = (sol >> (YZ_PRODUCT_VARS + 128)) & ((1 << 128) - 1)
        ok = True
        for pos, bit in enumerate(known):
            if bit == 1:
                y = parity_from_mask(y_state, all_masks[1][pos])
                z = parity_from_mask(z_state, all_masks[2][pos])
                if not (y or z):
                    ok = False
                    break
        if ok:
            yz_sol = (y_state, z_state, guessed, tries)
            break
        if yz_sol is not None:
            break

    if yz_sol is None:
        print('[!]   y/z recovery failed after', tries, 'guesses')
        return None

    y_state, z_state, guessed, tries = yz_sol
    print('[+]   recovered y/z after %d guesses; zero guess=%s' % (tries, guessed))

    x_eqs = []
    w_eqs = []
    for pos, bit in enumerate(known):
        y = parity_from_mask(y_state, all_masks[1][pos])
        z = parity_from_mask(z_state, all_masks[2][pos])
        if y == 0 and z == 1 and bit == 0:
            x_eqs.append((all_masks[0][pos], 1))
            w_eqs.append((all_masks[3][pos], 1))
            if len(x_eqs) >= 160 and len(w_eqs) >= 160:
                # A little slack above 128 makes the final linear solves robust.
                pass

    print('[+]   x/w linear samples:', len(x_eqs))
    x_state = solve_128_linear(x_eqs)
    w_state = solve_128_linear(w_eqs)
    if x_state is None or w_state is None:
        print('[!]   x/w recovery failed')
        return None

    key = int(x_state) | (int(y_state) << 128) | (int(z_state) << 256) | (int(w_state) << 384)
    return key


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description='Hyper512 solver (optimized)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tips:
  Start with default --nbits 2048.  If GB recovers <512 bits, increase:
    --nbits 4096   (safe bet, ~4x slower than 2048)
    --nbits 8192   (if still failing)
  The system has 3 equations per bit; 512 vars → ~170 bits is
  theoretically sufficient, but real GB needs ~2-4x overhead.
        """)
    ap.add_argument('--output', help='override output file path')
    ap.add_argument('--prefix', default='crypto{',
                    help='known flag prefix for extra known bits (default: crypto{)')
    ap.add_argument('--check', action='store_true',
                    help='verify layout/parsing only, do not solve')
    ap.add_argument('--nbits', type=int, default=32768,
                    help='number of known bits to use (default: 32768). '
                         'Fewer = faster GB; increase if <512 key bits recovered')
    ap.add_argument('--method', choices=['fca', 'linear', 'cms', 'sat', 'groebner'], default='fca',
                    help='solver backend (default: fca/writeup attack; linear is full linearization; cms uses CryptoMiniSat; sat uses Z3; groebner keeps the old Sage path)')
    ap.add_argument('--z3-timeout', type=int, default=0,
                    help='Z3 timeout in milliseconds, 0 means no timeout (default: 0)')
    ap.add_argument('--algorithm', default='libsingular:slimgb',
                    help='Groebner algorithm (default: libsingular:slimgb). '
                         'Use "default" for PolyBoRi/buchberger fallback.')
    args = ap.parse_args(argv)

    root = find_challenge_root()
    outpath = find_output_file(root, args.output)
    gift, ct = read_output(outpath)

    print('[+] challenge root:', root)
    print('[+] output file   :', outpath)
    print('[+] gift bytes    :', len(gift), '(%d bits)' % (len(gift)*8))
    print('[+] ct bytes      :', len(ct))

    prefix = args.prefix.encode() if args.prefix else b''
    known = list(bits_from_bytes(gift))
    if prefix:
        known += list(bits_from_bytes(
            bytes(bitxor(c, p) for c, p in zip(ct, prefix))))
        print('[+] prefix hint   :', prefix)

    # Clamp to --nbits
    if args.nbits < len(known):
        known = known[:args.nbits]
        print('[+] using bits    :', args.nbits, '(capped by --nbits)')
    else:
        print('[+] using bits    :', len(known), '(all available)')

    if args.check:
        print('[+] layout check OK — would use %d bits → ~%d equations'
              % (len(known), len(known)*3))
        return

    nbits = len(known)
    t_start = time.time()

    # ------------------------------------------------------------------
    # Step 1: Generate linear LFSR output masks
    # ------------------------------------------------------------------
    print('\n[+] Step 1/3: Generating LFSR linear masks for %d bits...' % nbits)
    t0 = time.time()
    all_masks = [gen_masks(MASKS[i], CALLS[i], nbits) for i in range(4)]
    print('[+]   done in %.1fs' % (time.time() - t0))

    if args.method == 'fca':
        print('\n[+] Step 2/3: Running fast-correlation style attack...')
        t0 = time.time()
        key = solve_fast_correlation(all_masks, known)
        print('[+]   FCA stage done in %.1fs' % (time.time() - t0))
        if key is None:
            print('[!] FCA attack failed.')
            print('[!] Try using all gift bits: --nbits %d' % (len(gift) * 8))
            return
        print('[+] key =', hex(key))
    elif args.method == 'linear':
        print('\n[+] Step 2/3: Solving linearized annihilator system...')
        t0 = time.time()
        key = solve_linearized(all_masks, known)
        print('[+]   linearized stage done in %.1fs' % (time.time() - t0))
        if key is None:
            print('[!] Linearized system did not fix all key bits.')
            print('[!] Try more bits, e.g. --nbits %d, or compare with --method cms'
                  % (args.nbits * 2))
            return
        print('[+] key =', hex(key))
    elif args.method == 'cms':
        print('\n[+] Step 2/3: Building CryptoMiniSat XOR/CNF constraints...')
        t0 = time.time()
        key = solve_with_cryptosat(all_masks, known)
        print('[+]   CMS stage done in %.1fs' % (time.time() - t0))
        if key is None:
            print('[!] CryptoMiniSat did not find a key.')
            print('[!] Try more bits, e.g. --nbits %d, or compare with --method sat'
                  % (args.nbits * 2))
            return
        print('[+] key =', hex(key))
    elif args.method == 'sat':
        print('\n[+] Step 2/3: Building SAT constraints...')
        t0 = time.time()
        key = solve_with_z3(all_masks, known, args.z3_timeout)
        print('[+]   SAT stage done in %.1fs' % (time.time() - t0))
        if key is None:
            print('[!] SAT solver did not find a key.')
            print('[!] Try more/less bits, e.g. --nbits %d, or add --z3-timeout 0'
                  % (args.nbits * 2))
            return
        print('[+] key =', hex(key))
    else:
        # ------------------------------------------------------------------
        # Step 2: Build Boolean quadratic system
        # ------------------------------------------------------------------
        print('\n[+] Step 2/3: Building Boolean quadratic equations...')
        t0 = time.time()
        B = BooleanPolynomialRing(512, 'k')
        ks = list(B.gens())
        ks0, ks1, ks2, ks3 = ks[0:128], ks[128:256], ks[256:384], ks[384:512]
        ZERO = B(0)
        ONE  = B(1)

        eqs = []
        for pos, bit in enumerate(known):
            xp = all_masks[0][pos]; yp = all_masks[1][pos]
            zp = all_masks[2][pos]; wp = all_masks[3][pos]

            x = lin(xp, ks0) or ZERO
            y = lin(yp, ks1) or ZERO
            z = lin(zp, ks2) or ZERO
            w = lin(wp, ks3) or ZERO

            # Boolean function annihilator equations (quadratic)
            if bit == 0:
                eqs.append(x*y + z + x*z + y*z)
                eqs.append(y + z + x*z + y*w)
                eqs.append(x*z + z*w)
            else:
                eqs.append(ONE + y + z + y*z)
                eqs.append(ONE + x + y + x*y + z + x*z + x*w + y*w)
                eqs.append(w + x*w + z*w)

            if pos and pos % 512 == 0:
                print('[+]   pos %d/%d  eqs=%d  t=%.1fs'
                      % (pos, nbits, len(eqs), time.time()-t0))

        n_eqs = len(eqs)
        print('[+]   total equations: %d  (built in %.1fs)' % (n_eqs, time.time()-t0))

        # ------------------------------------------------------------------
        # Step 3: Groebner basis
        # ------------------------------------------------------------------
        print('\n[+] Step 3/3: Computing Groebner basis...')
        print('[+]   algorithm:', args.algorithm)
        print('[+]   equations:', n_eqs, '  variables: 512')
        t0 = time.time()

        I = B.ideal(eqs)
        try:
            if args.algorithm == 'default':
                G = I.groebner_basis()
            else:
                G = I.groebner_basis(algorithm=args.algorithm)
        except Exception as e:
            print('[!]   algorithm failed (%s), retrying with default...' % e)
            G = I.groebner_basis()

        print('[+]   basis size: %d  (computed in %.1fs)' % (len(G), time.time()-t0))

        # ------------------------------------------------------------------
        # Extract key bits
        # ------------------------------------------------------------------
        sol = {}
        for g in G:
            if g.degree() == 1 and len(g.variables()) == 1:
                v = g.variables()[0]
                sol[v] = int(g.subs({v: 0}))

        print('[+] recovered key bits: %d / 512' % len(sol))

        if len(sol) < 512:
            print('[!] NOT ENOUGH - underdetermined system.')
            print('[!] Try: sage solve/solve_hyper512_fast.sage --nbits %d' % (args.nbits * 2))
            return

        key = 0
        for i, v in enumerate(ks):
            if sol.get(v):
                key |= 1 << i
        print('[+] key =', hex(key))

    # ------------------------------------------------------------------
    # Verify & decrypt
    # ------------------------------------------------------------------
    cipher = Cipher(key)
    gift2 = bytes(next(cipher.stream()) for _ in range(len(gift)))
    ok = gift2 == gift[:len(gift2)]   # verify against the original gift
    # If we only used nbits bits of gift, re-run cipher from scratch with full gift
    cipher2 = Cipher(key)
    gift_full = bytes(next(cipher2.stream()) for _ in range(len(gift)))
    print('[+] gift verifies:', gift_full == gift)
    if gift_full != gift:
        print('[!] key failed gift verification')
        return

    ks_bytes = bytes(next(cipher2.stream()) for _ in range(len(ct)))
    flag = bytes(bitxor(a, b) for a, b in zip(ct, ks_bytes))
    print('[+] flag =', flag)
    print('[+] total wall time: %.1fs' % (time.time() - t_start))


if __name__ == '__main__':
    main()
