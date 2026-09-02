#!/usr/bin/env python3
import argparse
import io
import math
import os
import socket
import sys
import zipfile
from multiprocessing import Pool, cpu_count
from pathlib import Path

E = 65537
DEFAULT_ROUNDS = 16384  # 1 flag + 4*16384 = 65537 commands
P2 = None
P3 = None


CPP_BATCH_GCD = r"""
#include <gmpxx.h>
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char** argv){
    if(argc < 3){ cerr << "usage: " << argv[0] << " Ds.txt hits.txt\n"; return 1; }
    ifstream in(argv[1]);
    if(!in){ cerr << "cannot open Ds input\n"; return 1; }
    vector<mpz_class> Ds;
    string s;
    while(in >> s){ mpz_class x; x.set_str(s, 16); Ds.push_back(x); }
    cerr << "[cpp] read " << Ds.size() << " D values\n";

    // Bernstein batch-GCD variant:
    // Build product tree of D_i^2. The root is P^2, so sqrt(root) gives
    // P=prod(D_i). Then use a remainder tree to compute P mod D_i^2.
    vector<vector<mpz_class>> tree;
    vector<mpz_class> level;
    level.reserve(Ds.size());
    for(auto &d: Ds) level.push_back(d*d);
    tree.push_back(std::move(level));

    while(tree.back().size() > 1){
        auto &prev = tree.back();
        vector<mpz_class> next;
        next.reserve((prev.size()+1)/2);
        for(size_t i=0;i<prev.size();i+=2){
            if(i+1 < prev.size()) next.push_back(prev[i]*prev[i+1]);
            else next.push_back(prev[i]);
        }
        tree.push_back(std::move(next));
    }

    mpz_class P;
    mpz_sqrt(P.get_mpz_t(), tree.back()[0].get_mpz_t());

    vector<mpz_class> rems;
    rems.push_back(P);
    for(int lvl=(int)tree.size()-2; lvl>=0; --lvl){
        vector<mpz_class> nr;
        nr.reserve(tree[lvl].size());
        for(size_t i=0;i<tree[lvl].size();i++){
            mpz_class r;
            mpz_mod(r.get_mpz_t(), rems[i/2].get_mpz_t(), tree[lvl][i].get_mpz_t());
            nr.push_back(std::move(r));
        }
        rems.swap(nr);
    }

    ofstream out(argv[2]);
    if(!out){ cerr << "cannot open hits output\n"; return 1; }
    int hits = 0;
    for(size_t i=0;i<Ds.size();i++){
        mpz_class quot = rems[i] / Ds[i];
        mpz_class g;
        mpz_gcd(g.get_mpz_t(), Ds[i].get_mpz_t(), quot.get_mpz_t());
        if(mpz_sizeinbase(g.get_mpz_t(), 2) > 400){
            out << i << " " << g.get_str(16) << "\n";
            hits++;
        }
    }
    cerr << "[cpp] hits " << hits << "\n";
    return 0;
}
"""


def i2b(x: int, length: int) -> bytes:
    return x.to_bytes(length, "big")


def pkcs7_unpad(x: bytes) -> bytes:
    if not x:
        raise ValueError("empty plaintext")
    n = x[-1]
    if n < 1 or n > 16 or x[-n:] != bytes([n]) * n:
        raise ValueError("bad PKCS#7 padding")
    return x[:-n]


def aes_cbc_decrypt_zero_iv(key: bytes, ct: bytes) -> bytes:
    # Prefer pycryptodome, fallback to cryptography.
    try:
        from Crypto.Cipher import AES
        return AES.new(key, AES.MODE_CBC, b"\x00" * 16).decrypt(ct)
    except ImportError:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        cipher = Cipher(algorithms.AES(key), modes.CBC(b"\x00" * 16))
        dec = cipher.decryptor()
        return dec.update(ct) + dec.finalize()


# ---------------------------------------------------------------------------
# Input: transcript.log, transcript.zip, or the outer challenge zip
# ---------------------------------------------------------------------------

def _read_log_from_zip_bytes(blob: bytes):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        for name in names:
            if name.endswith("transcript.log"):
                return z.read(name).decode()
        for name in names:
            if name.endswith(".zip") and "transcript" in name:
                got = _read_log_from_zip_bytes(z.read(name))
                if got is not None:
                    return got
    return None


def read_transcript_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    data = p.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(data)):
        txt = _read_log_from_zip_bytes(data)
        if txt is None:
            raise ValueError("zip file does not contain transcript.log")
        return txt
    return data.decode()


def parse_transcript_text(txt: str):
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    flag_ct = None
    rounds = []
    i = 0
    while i < len(lines):
        if lines[i] == "[cmd] flag":
            flag_ct = bytes.fromhex(lines[i + 1])
            i += 2
        elif lines[i] == "[cmd] pkey":
            if lines[i + 1] != "[cmd] send 2" or lines[i + 3] != "[cmd] send 3" or lines[i + 5] != "[cmd] backup":
                raise ValueError(f"unexpected transcript format around line {i}")
            c2 = int(lines[i + 2], 16)
            c3 = int(lines[i + 4], 16)
            cb = int(lines[i + 6], 16)
            rounds.append((c2, c3, cb))
            i += 7
        else:
            raise ValueError(f"unexpected line {i}: {lines[i]!r}")
    if flag_ct is None:
        raise ValueError("flag ciphertext not found")
    if not rounds:
        raise ValueError("no RSA rounds found")
    return flag_ct, rounds


# ---------------------------------------------------------------------------
# Optional remote collection. This sends exactly the same commands as the log.
# ---------------------------------------------------------------------------

def _recv_until(sock: socket.socket, marker: bytes) -> bytes:
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError("remote closed connection")
        buf += chunk
    return buf


def collect_remote(host: str, port: int, rounds: int = DEFAULT_ROUNDS):
    sock = socket.create_connection((host, port))
    sock.settimeout(20)
    _recv_until(sock, b"[cmd] ")

    def run(cmd: str):
        sock.sendall(cmd.encode() + b"\n")
        data = _recv_until(sock, b"[cmd] ")
        # Remove the next prompt. Keep only output produced by the command.
        if data.endswith(b"[cmd] "):
            data = data[:-6]
        return [x.strip().decode() for x in data.replace(b"\r\n", b"\n").split(b"\n") if x.strip()]

    out = run("flag")
    if len(out) != 1:
        raise ValueError(f"unexpected flag response: {out!r}")
    flag_ct = bytes.fromhex(out[0])

    triples = []
    for idx in range(rounds):
        run("pkey")
        c2 = int(run("send 2")[-1], 16)
        c3 = int(run("send 3")[-1], 16)
        cb = int(run("backup")[-1], 16)
        triples.append((c2, c3, cb))
        if (idx + 1) % 512 == 0:
            print(f"[+] collected {idx + 1}/{rounds} rounds", file=sys.stderr, flush=True)
    sock.close()
    return flag_ct, triples


# ---------------------------------------------------------------------------
# Crypto attack
# ---------------------------------------------------------------------------

def _init_worker():
    global P2, P3
    P2 = 1 << E
    P3 = pow(3, E)


def _recover_D_one(triple):
    c2, c3, _ = triple
    # n divides both values because c2 = 2^e mod n and c3 = 3^e mod n.
    # The gcd is normally k*n where k is a small random cofactor.
    return math.gcd(P2 - c2, P3 - c3)


def recover_Ds(rounds, jobs: int = 1):
    if jobs <= 1:
        _init_worker()
        Ds = []
        for i, r in enumerate(rounds):
            Ds.append(_recover_D_one(r))
            if (i + 1) % 1024 == 0:
                print(f"[+] recovered D for {i + 1}/{len(rounds)} rounds", file=sys.stderr, flush=True)
        return Ds
    with Pool(processes=jobs, initializer=_init_worker) as pool:
        Ds = []
        for i, D in enumerate(pool.imap(_recover_D_one, rounds, chunksize=64)):
            Ds.append(D)
            if (i + 1) % 1024 == 0:
                print(f"[+] recovered D for {i + 1}/{len(rounds)} rounds", file=sys.stderr, flush=True)
        return Ds


def read_D_cache(path: str):
    out = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(int(line, 16))
    return out


def write_D_cache(path: str, Ds):
    with open(path, "w") as f:
        for x in Ds:
            f.write(hex(x)[2:] + "\n")


def _run_cpp_batch_gcd(Ds):
    """Fast path: compile and run a tiny GMP C++ batch-GCD helper."""
    import shutil
    import subprocess
    import tempfile

    if shutil.which("g++") is None:
        raise RuntimeError("g++ not found")

    with tempfile.TemporaryDirectory(prefix="kbs2_") as td:
        td = Path(td)
        src = td / "batch_gcd.cpp"
        exe = td / "batch_gcd"
        ds_path = td / "Ds.txt"
        hits_path = td / "hits.txt"
        src.write_text(CPP_BATCH_GCD)
        write_D_cache(str(ds_path), Ds)

        compile_cmd = ["g++", "-O3", "-std=c++17", str(src), "-lgmpxx", "-lgmp", "-o", str(exe)]
        subprocess.run(compile_cmd, check=True)
        subprocess.run([str(exe), str(ds_path), str(hits_path)], check=True)

        hits = []
        for line in hits_path.read_text().splitlines():
            idx_s, g_s = line.split()
            hits.append((int(idx_s), int(g_s, 16)))
        return hits


def _product_balanced(vals):
    vals = list(vals)
    if not vals:
        return 1
    while len(vals) > 1:
        vals = [vals[i] * vals[i + 1] if i + 1 < len(vals) else vals[i]
                for i in range(0, len(vals), 2)]
    return vals[0]


def _find_shared_factor_hits_slow_python(Ds):
    # This fallback is intentionally simple. For the full 16384-round transcript,
    # the C++/GMP helper is much faster.
    print("[+] C++/GMP unavailable; using slower Python batch GCD", file=sys.stderr, flush=True)
    P = _product_balanced(Ds)
    hits = []
    for i, D in enumerate(Ds):
        g = math.gcd(D, P // D)
        if g.bit_length() > 400:
            hits.append((i, g))
            print(f"[+] hit at round {i}: shared factor candidate has {g.bit_length()} bits", file=sys.stderr, flush=True)
    return hits


def find_shared_factor_hits(Ds):
    print("[+] running batch GCD", file=sys.stderr, flush=True)
    try:
        hits = _run_cpp_batch_gcd(Ds)
    except Exception as e:
        print(f"[!] C++/GMP fast path failed: {e}", file=sys.stderr, flush=True)
        hits = _find_shared_factor_hits_slow_python(Ds)

    for i, g in hits:
        print(f"[+] hit at round {i}: shared factor candidate has {g.bit_length()} bits", file=sys.stderr, flush=True)
    return hits


def try_decrypt_from_hits(flag_ct: bytes, rounds, Ds, hits, max_shared_cofactor: int, max_D_multiplier: int):
    for idx, g in hits:
        c2, c3, cb = rounds[idx]
        # g is p times a small cofactor. Strip the small cofactor by brute force.
        for small in range(1, max_shared_cofactor + 1):
            if g % small:
                continue
            p = g // small
            if not (500 <= p.bit_length() <= 513):
                continue

            # D = k*n = k*p*q.  Since ciphertexts are < n, k < D/max(ciphertexts).
            bound_from_ct = Ds[idx] // max(c2, c3, cb) + 3
            k_bound = min(max_D_multiplier, max(1, bound_from_ct))
            for k in range(1, k_bound + 1):
                kp = k * p
                if Ds[idx] % kp:
                    continue
                q = Ds[idx] // kp
                if not (500 <= q.bit_length() <= 513):
                    continue
                n = p * q
                if pow(2, E, n) != c2 or pow(3, E, n) != c3:
                    continue

                phi = (p - 1) * (q - 1)
                d = pow(E, -1, phi)
                master_int = pow(cb, d, n)
                if master_int >= (1 << 256):
                    continue
                master = i2b(master_int, 32)
                pt = aes_cbc_decrypt_zero_iv(master, flag_ct)
                try:
                    flag = pkcs7_unpad(pt).decode()
                except Exception:
                    continue
                if flag.startswith("hkcert") or "{" in flag:
                    return {
                        "round": idx,
                        "p": p,
                        "q": q,
                        "small_cofactor": small,
                        "D_multiplier": k,
                        "master_secret": master,
                        "padded_plaintext": pt,
                        "flag": flag,
                    }
    return None


def solve(flag_ct, rounds, ds_cache=None, jobs=1, max_shared_cofactor=1 << 20, max_D_multiplier=1 << 20):
    if ds_cache and os.path.exists(ds_cache):
        print(f"[+] reading D cache: {ds_cache}", file=sys.stderr, flush=True)
        Ds = read_D_cache(ds_cache)
        if len(Ds) != len(rounds):
            raise ValueError(f"D cache has {len(Ds)} values, but transcript has {len(rounds)} rounds")
    else:
        print(f"[+] recovering modulus multiples from {len(rounds)} rounds", file=sys.stderr, flush=True)
        Ds = recover_Ds(rounds, jobs=jobs)
        if ds_cache:
            print(f"[+] writing D cache: {ds_cache}", file=sys.stderr, flush=True)
            write_D_cache(ds_cache, Ds)

    hits = find_shared_factor_hits(Ds)
    print(f"[+] total large shared-factor hits: {len(hits)}", file=sys.stderr, flush=True)
    ans = try_decrypt_from_hits(flag_ct, rounds, Ds, hits, max_shared_cofactor, max_D_multiplier)
    if ans is None:
        raise RuntimeError("exploit failed; try increasing --max-shared-cofactor or --max-D-multiplier")
    return ans


def main():
    ap = argparse.ArgumentParser(description="Solver for HKCERT CTF 2021 - Key Backup Service 2")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--transcript", help="path to transcript.log, transcript.zip, or the outer challenge zip")
    src.add_argument("--host", help="remote host; requires --port")
    ap.add_argument("--port", type=int, help="remote port")
    ap.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS, help="remote rounds to collect")
    ap.add_argument("--jobs", type=int, default=max(1, min(cpu_count(), 4)), help="parallel workers for gcd recovery")
    ap.add_argument("--ds-cache", default="Ds_cache.txt", help="cache file for recovered gcd values")
    ap.add_argument("--max-shared-cofactor", type=int, default=1 << 20)
    ap.add_argument("--max-D-multiplier", type=int, default=1 << 20)
    args = ap.parse_args()

    if args.host:
        if args.port is None:
            ap.error("--host requires --port")
        flag_ct, rounds = collect_remote(args.host, args.port, rounds=args.rounds)
    else:
        txt = read_transcript_text(args.transcript)
        flag_ct, rounds = parse_transcript_text(txt)

    print(f"[+] flag ciphertext: {flag_ct.hex()}", file=sys.stderr)
    print(f"[+] RSA rounds: {len(rounds)}", file=sys.stderr)

    ans = solve(
        flag_ct,
        rounds,
        ds_cache=args.ds_cache,
        jobs=args.jobs,
        max_shared_cofactor=args.max_shared_cofactor,
        max_D_multiplier=args.max_D_multiplier,
    )

    print("[+] FOUND")
    print(f"round = {ans['round']}")
    print(f"small_cofactor = {ans['small_cofactor']}")
    print(f"D_multiplier = {ans['D_multiplier']}")
    print(f"master_secret = {ans['master_secret'].hex()}")
    print(f"p = {hex(ans['p'])}")
    print(f"q = {hex(ans['q'])}")
    print(f"flag = {ans['flag']}")


if __name__ == "__main__":
    main()
