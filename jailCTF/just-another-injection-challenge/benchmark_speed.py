import socket
import time
import solve_remote_live, json

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def benchmark_batch(batch_size=64):
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    buf = buf.split(b"expr: ", 1)[1]
    
    # Build batch of dummy length queries
    exprs = []
    for i in range(batch_size):
        v = (i % 30) + 1
        if v not in CHAINS: v = 1
        pred = predicate(CHAINS[v])
        exprs.append(f"env|keys|length|{pred}|error")
        
    t0 = time.time()
    s.sendall(("\n".join(exprs) + "\n").encode())
    
    answers = []
    token_re = solve_remote_live.TOKEN_RE
    while len(answers) < len(exprs):
        matches = list(token_re.finditer(buf))
        if matches:
            take = min(len(matches), len(exprs) - len(answers))
            answers.extend(m.group(1).decode() for m in matches[:take])
            buf = buf[matches[take - 1].end():]
            if len(answers) == len(exprs):
                break
            continue
        chunk = s.recv(65536)
        if not chunk: break
        buf += chunk
        
    t1 = time.time()
    s.close()
    
    dt = t1 - t0
    qps = len(exprs) / dt if dt > 0 else 0
    print(f"[+] Executed {len(exprs)} queries in {dt:.3f}s -> {qps:.1f} queries/second!")

if __name__ == "__main__":
    benchmark_batch(64)
