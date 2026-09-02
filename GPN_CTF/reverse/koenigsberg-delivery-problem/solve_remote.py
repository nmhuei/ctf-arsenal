#!/usr/bin/env python3
import argparse
import re
import socket
import ssl
import struct
import subprocess
import sys
from collections import defaultdict

CFG_START = 0x1190
CFG_END = 0x40E1
RO_ADDR = 0x6000
RO_SIZE = 0x186CC
DEFAULT_HOST = "pan-seared-celery-beside-smashed-ice-cream-yaog.gpn24.ctf.kitctf.de"
DEFAULT_PORT = 443


def parse_binary(bin_path: str):
    out = subprocess.check_output(["objdump", "-d", "-M", "intel", bin_path], text=True)
    insns = []
    for line in out.splitlines():
        m = re.match(r"^\s*([0-9a-f]+):\s+([0-9a-f][0-9a-f] )+", line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        txt = line.split("\t")[-1].strip()
        insns.append((addr, txt))

    cfg_insns = [x for x in insns if CFG_START <= x[0] < CFG_END]
    starts = []
    for i, (_addr, txt) in enumerate(cfg_insns):
        if txt.startswith("inc    BYTE PTR [rsp") and i + 6 < len(cfg_insns):
            if "movzx  edx,BYTE PTR [rdi+rcx*1]" in cfg_insns[i + 1][1]:
                starts.append(i)

    data = open(bin_path, "rb").read()
    ro = data[RO_ADDR:RO_ADDR + RO_SIZE]

    states = []
    for i in starts:
        addr, txt = cfg_insns[i]
        m = re.search(r"inc    BYTE PTR \[rsp(?:\+0x([0-9a-f]+))?\]", txt)
        if not m:
            raise RuntimeError(f"could not parse state id at {addr:#x}")
        sid = int(m.group(1), 16) if m.group(1) else 0

        m = re.search(r"cmp    rdx,0x([0-9a-f]+)", cfg_insns[i + 2][1])
        if not m:
            raise RuntimeError(f"could not parse max label at {addr:#x}")
        mx = int(m.group(1), 16)

        if "movsxd rdx,DWORD PTR [rax+rdx*4]" in cfg_insns[i + 5][1]:
            table = 0x6004
        else:
            m = re.search(r"# ([0-9a-f]+) ", cfg_insns[i + 5][1])
            if not m:
                raise RuntimeError(f"could not parse jump table at {addr:#x}")
            table = int(m.group(1), 16)

        states.append({"id": sid, "addr": addr, "max": mx, "table": table})

    if len(states) != 250:
        raise RuntimeError(f"expected 250 states, got {len(states)}")

    addr_to_state = {s["addr"]: s["id"] for s in states}
    adj = defaultdict(list)
    edge_label = {}

    for s in states:
        base = s["table"]
        for x in range(s["max"] + 1):
            rel = struct.unpack_from("<i", ro, base - RO_ADDR + x * 4)[0]
            target_addr = base + rel
            nxt = addr_to_state[target_addr]
            adj[s["id"]].append(nxt)
            edge_label.setdefault((s["id"], nxt), x)

    for u in list(adj):
        dedup = []
        seen = set()
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            dedup.append(v)
        adj[u] = dedup

    return states, adj, edge_label


def find_path(adj, start=0, n=250):
    sys.setrecursionlimit(10000)
    visited = [False] * n
    visited[start] = True
    path = [start]
    outdeg = {u: len(adj[u]) for u in range(n)}

    def dfs(u, depth):
        if depth == n:
            return True
        nbrs = [v for v in adj[u] if not visited[v]]
        nbrs.sort(key=lambda v: outdeg[v])
        for v in nbrs:
            visited[v] = True
            path.append(v)
            if dfs(v, depth + 1):
                return True
            path.pop()
            visited[v] = False
        return False

    if not dfs(start, 1):
        raise RuntimeError("no Hamiltonian path found")
    return path


def build_payload(edge_label, path):
    labels = [edge_label[(a, b)] for a, b in zip(path, path[1:])]
    labels.append(-1)
    return ";".join(map(str, labels)) + ";"


def tls_send(host: str, port: int, payload: str, timeout: int = 10):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with socket.create_connection((host, port), timeout=timeout) as raw:
        with ctx.wrap_socket(raw, server_hostname=host) as s:
            s.sendall(payload.encode())
            s.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
    return b"".join(chunks).decode(errors="replace")


def main():
    ap = argparse.ArgumentParser(description="Solve koenigsberg-delivery-problem locally and send to remote over TLS")
    ap.add_argument("binary", nargs="?", default="cartographer", help="path to the challenge binary")
    ap.add_argument("host", nargs="?", default=DEFAULT_HOST, help="remote host")
    ap.add_argument("port", nargs="?", default=DEFAULT_PORT, type=int, help="remote port")
    ap.add_argument("--payload-only", action="store_true", help="only print the generated payload")
    args = ap.parse_args()

    states, adj, edge_label = parse_binary(args.binary)
    path = find_path(adj)
    payload = build_payload(edge_label, path)

    print(f"[+] parsed states: {len(states)}")
    print(f"[+] path length: {len(path)} unique={len(set(path))}")
    print(f"[+] payload tokens: {len([x for x in payload.split(';') if x])}")

    if args.payload_only:
        print(payload)
        return

    print(f"[+] connecting to {args.host}:{args.port}")
    reply = tls_send(args.host, args.port, payload)
    print("[+] server reply:")
    print(reply)


if __name__ == "__main__":
    main()
