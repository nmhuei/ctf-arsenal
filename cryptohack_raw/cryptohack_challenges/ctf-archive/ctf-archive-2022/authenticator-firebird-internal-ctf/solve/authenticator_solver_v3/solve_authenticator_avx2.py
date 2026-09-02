#!/usr/bin/env python3
import argparse
import os
import random
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

PROMPT1 = b"challenge_client = "
PROMPT2 = b"response_client = "
ZERO_CHALLENGE = "00" * 16
TOTAL_PAIRS = 62 * 61
HEX64 = re.compile(rb"response_server = ([0-9a-f]{64})")
HEX32 = re.compile(rb"challenge_server = ([0-9a-f]{32})")
RESP = re.compile(r"response_client=([0-9a-f]{64})")
PW = re.compile(r"password=([0-9A-Za-z]{6})")
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Minimal BLAKE3 one-block implementation for self-test only.
IV = [0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
PERM = [2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]

def _rotr(x, n):
    return ((x >> n) | ((x << (32 - n)) & 0xffffffff)) & 0xffffffff

def _g(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & 0xffffffff; v[d] = _rotr(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & 0xffffffff; v[b] = _rotr(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & 0xffffffff; v[d] = _rotr(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & 0xffffffff; v[b] = _rotr(v[b] ^ v[c], 7)

def _round(v, m):
    _g(v,0,4,8,12,m[0],m[1]); _g(v,1,5,9,13,m[2],m[3]); _g(v,2,6,10,14,m[4],m[5]); _g(v,3,7,11,15,m[6],m[7])
    _g(v,0,5,10,15,m[8],m[9]); _g(v,1,6,11,12,m[10],m[11]); _g(v,2,7,8,13,m[12],m[13]); _g(v,3,4,9,14,m[14],m[15])

def blake3_oneblock_digest(msg: bytes) -> bytes:
    if len(msg) > 64:
        raise ValueError("self-test helper only supports one block")
    block = msg + b"\0" * (64 - len(msg))
    m = [int.from_bytes(block[4*i:4*i+4], "little") for i in range(16)]
    v = IV[:] + IV[:4] + [0, 0, len(msg), 1 | 2 | 8]  # CHUNK_START | CHUNK_END | ROOT
    for _ in range(7):
        _round(v, m)
        m = [m[i] for i in PERM]
    return b"".join(((v[i] ^ v[i+8]) & 0xffffffff).to_bytes(4, "little") for i in range(8))


def recv_until(sock: socket.socket, marker: bytes, timeout: float = 15.0) -> bytes:
    sock.settimeout(timeout)
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError(data.decode(errors="replace"))
        data += chunk
    return data


def cpu_flags() -> str:
    try:
        text = Path("/proc/cpuinfo").read_text(errors="ignore")
        m = re.search(r"^flags\s*:\s*(.*)$", text, re.M)
        return m.group(1) if m else text
    except OSError:
        return ""


def build_cracker(root: Path) -> Path:
    src = root / "crack_auth_avx2.c"
    bin_path = root / "crack_auth_avx2"
    if bin_path.exists() and bin_path.stat().st_mtime >= src.stat().st_mtime:
        return bin_path
    cmd = ["gcc", "-O3", "-mavx2", "-fopenmp", str(src), "-o", str(bin_path)]
    print("[*] compiling AVX2 cracker...", flush=True)
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        raise SystemExit("[-] gcc not found. Install gcc/libgomp or run on a Linux box with gcc.")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"[-] compile failed: {e}")
    return bin_path


def run_cracker(bin_path: Path, target_hex: str, challenge_server_hex: str, pair_start: int, pair_count: int, threads: int, timeout: float | None = None):
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    cmd = [str(bin_path), target_hex, challenge_server_hex, str(pair_start), str(pair_count)]
    return subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)


def explain_bad_return(p: subprocess.CompletedProcess) -> str:
    pieces = [f"cracker exited with code {p.returncode}"]
    if p.returncode in (-4, 132):
        pieces.append("this usually means Illegal instruction: your CPU/VM does not expose AVX2")
    if p.stdout.strip():
        pieces.append("stdout:\n" + p.stdout.strip())
    if p.stderr.strip():
        pieces.append("stderr:\n" + p.stderr.strip())
    return "\n".join(pieces)


def self_test(bin_path: Path, threads: int) -> None:
    # password 0Zabcd lies in first-two-char pair index 60.
    pw = b"0Zabcd"
    challenge_client = bytes(16)
    target = blake3_oneblock_digest(pw + b"HANDSHAKE_FROM_SERVER" + challenge_client).hex()
    p = run_cracker(bin_path, target, "00" * 16, 60, 1, threads, timeout=10)
    sys.stderr.write(p.stderr)
    if p.returncode != 0 or "password=0Zabcd" not in p.stdout:
        raise SystemExit("[-] cracker self-test failed.\n" + explain_bad_return(p))
    print("[*] self-test OK", flush=True)


def calibrate(bin_path: Path, threads: int, target_seconds: float) -> int:
    # A not-found target makes the cracker scan the full requested slice. Return code 2 is expected.
    probe_pairs = 4
    t0 = time.time()
    p = run_cracker(bin_path, "00" * 32, "00" * 16, 0, probe_pairs, threads, timeout=max(20.0, target_seconds + 5.0))
    elapsed = time.time() - t0
    sys.stderr.write(p.stderr)
    if p.returncode != 2:
        raise SystemExit("[-] calibration failed.\n" + explain_bad_return(p))
    per_pair = elapsed / probe_pairs
    if per_pair <= 0.0001:
        raise SystemExit(f"[-] calibration time is suspiciously small ({per_pair:.6f}s/pair); not trusting it")
    pairs = int(target_seconds / per_pair)
    pairs = max(1, min(pairs, TOTAL_PAIRS))
    print(f"[*] calibration: {per_pair:.4f}s/pair, using {pairs}/{TOTAL_PAIRS} pairs per attempt (~{100*pairs/TOTAL_PAIRS:.2f}% success/attempt)", flush=True)
    if pairs < 25:
        print("[!] This CPU is slow for the 10s server limit; raise --threads, try bare metal, or use a faster CPU/GPU.", flush=True)
    return pairs


def try_once(host: str, port: int, bin_path: Path, threads: int, pair_start: int, pair_count: int, crack_timeout: float) -> bool:
    with socket.create_connection((host, port), timeout=10) as s:
        banner = recv_until(s, PROMPT1)
        s.sendall((ZERO_CHALLENGE + "\n").encode())
        data = recv_until(s, PROMPT2)
        blob = banner + data
        m_rs = HEX64.search(blob)
        m_cs = HEX32.search(blob)
        if not (m_rs and m_cs):
            print(blob.decode(errors="replace"))
            raise RuntimeError("could not parse server response")
        response_server = m_rs.group(1).decode()
        challenge_server = m_cs.group(1).decode()

        p = run_cracker(bin_path, response_server, challenge_server, pair_start, pair_count, threads, timeout=crack_timeout)
        sys.stderr.write(p.stderr)
        if p.returncode not in (0, 2):
            raise RuntimeError(explain_bad_return(p))
        if p.returncode == 2:
            return False
        m = RESP.search(p.stdout)
        if not m:
            raise RuntimeError("cracker found a password but no response_client was printed\n" + p.stdout)
        response_client = m.group(1)
        print(p.stdout, end="", flush=True)
        s.sendall((response_client + "\n").encode())
        try:
            final = s.recv(4096).decode(errors="replace")
        except socket.timeout:
            final = ""
        print(final, flush=True)
        return "Congrats" in final or "flag" in final.lower() or "{" in final


def main() -> None:
    ap = argparse.ArgumentParser(description="AVX2 solver for CryptoHack Authenticator / Firebird Internal CTF")
    ap.add_argument("host", nargs="?", default="archive.cryptohack.org")
    ap.add_argument("port", nargs="?", type=int, default=40156)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("OMP_NUM_THREADS", "4")))
    ap.add_argument("--pairs", type=int, default=0, help="pairs per connection; 0 = calibrate")
    ap.add_argument("--seconds", type=float, default=7.0, help="local cracking budget per connection; keep under server 10s alarm")
    ap.add_argument("--max-attempts", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--no-selftest", action="store_true")
    ap.add_argument("--random-start", action="store_true", help="randomize pair_start each attempt")
    args = ap.parse_args()

    flags = cpu_flags()
    if flags and "avx2" not in flags:
        raise SystemExit("[-] This solver requires AVX512F. Your CPU/VM does not advertise avx512f.\n"
                         "    Run it on an AVX2-capable machine/VM or use a GPU implementation.")

    root = Path(__file__).resolve().parent
    bin_path = build_cracker(root)
    if not args.no_selftest:
        self_test(bin_path, args.threads)
    pair_count = args.pairs or calibrate(bin_path, args.threads, args.seconds)
    crack_timeout = min(9.2, args.seconds + 1.2)

    attempt = 0
    while args.max_attempts <= 0 or attempt < args.max_attempts:
        if args.random_start:
            pair_start = random.randrange(TOTAL_PAIRS)
        else:
            pair_start = (attempt * pair_count) % TOTAL_PAIRS
        attempt += 1
        print(f"[*] attempt {attempt}: pair_start={pair_start}, pair_count={pair_count}", flush=True)
        try:
            if try_once(args.host, args.port, bin_path, args.threads, pair_start, pair_count, crack_timeout):
                return
        except subprocess.TimeoutExpired:
            print("[!] local crack timed out; lower --seconds or --pairs", flush=True)
        except (OSError, EOFError, RuntimeError) as e:
            print(f"[!] attempt failed: {e}", flush=True)
        time.sleep(0.10)

    raise SystemExit("[-] no flag; this is probabilistic, increase --max-attempts or run on faster hardware")

if __name__ == "__main__":
    main()
