#!/usr/bin/env python3
"""
Solver for koenigsberg-delivery-problem.

Usage:
  python3 solve.py local ./koenigsberg-delivery-problem/cartographer
  python3 solve.py remote pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de 443
  python3 solve.py payload > payload.txt
"""
import socket
import ssl
import subprocess
import sys

# 249 valid transition labels forming a Hamiltonian path over the 250 CFG states,
# plus 127 as the final invalid label to force cfg() into check_instance().
LABELS = [39, 11, 35, 62, 68, 27, 23, 69, 10, 24, 86, 70, 19, 16, 50, 38, 42, 55, 88, 70, 57, 44, 18, 36, 38, 76, 63, 69, 6, 37, 8, 3, 48, 58, 83, 11, 84, 74, 88, 5, 11, 63, 51, 88, 11, 59, 28, 8, 47, 6, 3, 41, 26, 17, 72, 34, 64, 3, 45, 67, 80, 55, 16, 52, 29, 88, 70, 89, 6, 84, 68, 8, 19, 86, 29, 23, 74, 71, 56, 99, 55, 53, 78, 19, 10, 88, 67, 97, 69, 64, 40, 55, 56, 77, 25, 46, 80, 38, 73, 71, 92, 38, 61, 16, 29, 74, 11, 84, 44, 100, 62, 22, 2, 62, 29, 14, 18, 84, 47, 24, 104, 14, 89, 60, 41, 82, 63, 2, 77, 44, 61, 56, 78, 43, 48, 92, 70, 82, 32, 11, 66, 104, 83, 14, 13, 44, 5, 52, 74, 26, 18, 16, 66, 100, 29, 21, 66, 34, 49, 104, 9, 4, 36, 81, 99, 89, 6, 67, 7, 74, 100, 37, 3, 39, 101, 11, 0, 83, 102, 53, 90, 91, 1, 93, 29, 62, 51, 96, 38, 75, 48, 26, 107, 33, 72, 5, 59, 22, 73, 83, 5, 77, 55, 77, 40, 94, 24, 39, 48, 33, 38, 58, 12, 45, 18, 22, 26, 56, 52, 21, 43, 22, 68, 35, 75, 101, 87, 68, 71, 73, 61, 5, 94, 24, 100, 6, 31, 45, 64, 36, 1, 59, 38, 31, 69, 72, 30, 31, 27, 127]


def payload() -> bytes:
    assert len(LABELS) == 250
    assert all(0 <= x <= 127 for x in LABELS)
    return (";".join(map(str, LABELS)) + ";\n").encode()


def local(binary: str) -> int:
    p = subprocess.run([binary], input=payload(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout.buffer.write(p.stdout)
    sys.stderr.buffer.write(p.stderr)
    return p.returncode


def remote(host: str, port: int) -> int:
    ctx = ssl.create_default_context()
    try:
        raw = socket.create_connection((host, port), timeout=15)
        s = ctx.wrap_socket(raw, server_hostname=host)
    except ssl.SSLError:
        raw = socket.create_connection((host, port), timeout=15)
        s = ssl._create_unverified_context().wrap_socket(raw, server_hostname=host)
    s.settimeout(8)
    s.sendall(payload())
    out = bytearray()
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
    except socket.timeout:
        pass
    finally:
        s.close()
    sys.stdout.buffer.write(out)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"local", "remote", "payload"}:
        print(__doc__.strip(), file=sys.stderr)
        raise SystemExit(2)
    if sys.argv[1] == "payload":
        sys.stdout.buffer.write(payload())
    elif sys.argv[1] == "local":
        if len(sys.argv) != 3:
            raise SystemExit("usage: python3 solve.py local ./cartographer")
        raise SystemExit(local(sys.argv[2]))
    else:
        if len(sys.argv) != 4:
            raise SystemExit("usage: python3 solve.py remote HOST PORT")
        raise SystemExit(remote(sys.argv[2], int(sys.argv[3])))
