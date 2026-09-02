import socket
import re
import sys

def query(expr):
    s = socket.create_connection(("challs.pyjail.club", 20219), timeout=5)
    buf = b""
    while b"expr: " not in buf:
        chunk = s.recv(4096)
        if not chunk:
            break
        buf += chunk
    
    # send expression
    s.sendall(expr.encode() + b"\n")
    
    # read response
    buf = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        buf += chunk
        if b"ok" in buf or b"error" in buf or b"blocked" in buf:
            break
    s.close()
    
    res = buf.decode(errors="replace")
    for word in ["ok", "error", "blocked"]:
        if word in res:
            return word
    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"Query: {sys.argv[1]}")
        print(f"Result: {query(sys.argv[1])}")
