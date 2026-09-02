#!/usr/bin/env python3
import argparse
import io
import os
import re
import tarfile
from pathlib import Path

import numpy as np

FLAG_RE = re.compile(r"GPNCTF\{[^}\n\r]*\}")


def load_data(path: Path) -> bytes:
    raw = path.read_bytes()
    if tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as tf:
            members = [m for m in tf.getmembers() if m.isfile()]
            if len(members) != 1:
                raise RuntimeError(f"expected one data file in tar, got {len(members)}")
            f = tf.extractfile(members[0])
            if f is None:
                raise RuntimeError("could not extract member")
            raw = f.read()
            print(f"[+] extracted {members[0].name}: {len(raw)} bytes")
    else:
        print(f"[+] loaded raw data: {len(raw)} bytes")
    return raw


def divisors(n: int, lo: int, hi: int):
    out = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            if lo <= d <= hi:
                out.append(d)
            q = n // d
            if q != d and lo <= q <= hi:
                out.append(q)
        d += 1
    return sorted(out)


def bits_to_values(bits, nbits, off, order):
    vals = []
    positions = []
    for i in range(off, len(bits) - nbits + 1, nbits):
        v = 0
        if order == "lsb":
            for k in range(nbits):
                v |= bits[i + k] << k
        else:
            for k in range(nbits):
                v = (v << 1) | bits[i + k]
        vals.append(v)
        positions.append(i)
    tail = bits[off + len(vals) * nbits:]
    return vals, positions, tail


def printable_from_vals(vals, mask):
    chars = []
    for v in vals:
        c = v & mask
        chars.append(chr(c) if 32 <= c < 127 else ".")
    return "".join(chars)


def try_tail_char(tail, nbits, order, mask):
    if not tail:
        return ""
    # The final encoded character may be truncated. Pad missing high bits with zero.
    # For LSB-first storage, existing bits are the low bits. For MSB-first, append zeros.
    if order == "lsb":
        v = 0
        for k, bit in enumerate(tail):
            v |= bit << k
    else:
        v = 0
        for bit in tail:
            v = (v << 1) | bit
        v <<= (nbits - len(tail))
    c = v & mask
    return chr(c) if 32 <= c < 127 else ""


def decode_candidate(bits, unit, *, verbose=False):
    transforms = []
    for rev in (False, True):
        seq = bits[::-1] if rev else bits[:]
        for inv in (False, True):
            seq2 = [1 - b for b in seq] if inv else seq
            transforms.append((rev, inv, seq2))

    for rev, inv, seq in transforms:
        for nbits in range(5, 17):
            for order in ("lsb", "msb"):
                for off in range(nbits):
                    vals, positions, tail = bits_to_values(seq, nbits, off, order)
                    for mask in (0x7f, 0xff):
                        s = printable_from_vals(vals, mask)
                        extra = try_tail_char(tail, nbits, order, mask)
                        candidate_text = s + extra
                        m = FLAG_RE.search(candidate_text)
                        if m:
                            info = {
                                "unit": unit,
                                "rev": rev,
                                "inv": inv,
                                "nbits": nbits,
                                "order": order,
                                "off": off,
                                "mask": mask,
                                "text": candidate_text,
                                "tail_bits": "".join(map(str, tail)),
                            }
                            return m.group(0), info
    return None, None


def main():
    ap = argparse.ArgumentParser(description="Solve the organized CTF challenge")
    ap.add_argument("path", nargs="?", default="organized.tar.gz", help="archive or raw data file")
    ap.add_argument("--min-unit", type=int, default=1000)
    ap.add_argument("--max-unit", type=int, default=100000)
    args = ap.parse_args()

    raw = load_data(Path(args.path))
    a = np.frombuffer(raw, dtype=np.uint8)
    print(f"[+] total bytes: {len(a)}")

    for unit in divisors(len(a), args.min_unit, args.max_unit):
        nblocks = len(a) // unit
        if nblocks < 32:
            continue
        # Need enough bits to hold the encoded flag.
        blocks = a.reshape(nblocks, unit)
        means = blocks.mean(axis=1)
        if float(means.max() - means.min()) < 40:
            continue
        threshold = float((means.max() + means.min()) / 2.0)
        bits = [int(x > threshold) for x in means]
        flag, info = decode_candidate(bits, unit)
        if flag:
            print(f"[+] block unit: {unit} bytes")
            print(f"[+] blocks: {nblocks}")
            print(f"[+] mean range: {means.min():.2f} .. {means.max():.2f}; threshold={threshold:.2f}")
            print(f"[+] first 64 bits: {''.join(map(str, bits[:64]))}")
            print(
                "[+] decode params: "
                f"nbits={info['nbits']} order={info['order']} offset={info['off']} "
                f"mask=0x{info['mask']:x} rev={info['rev']} inv={info['inv']}"
            )
            if info["tail_bits"]:
                print(f"[+] tail bits padded for final char: {info['tail_bits']}")
            print(f"[+] decoded text: {info['text']}")
            print(f"FLAG: {flag}")
            return

    raise SystemExit("[-] no flag found")


if __name__ == "__main__":
    main()
