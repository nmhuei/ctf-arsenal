#!/usr/bin/env python3
import socket
import time
import sys

HOST = "34.2.147.230"
PORT = 7000

ANSWERS = [
    ("Q1: Victim IP", "192.168.100.10"),
    ("Q2: User-Agent versioning artifact", "5.1.26100.8521"),
    ("Q3: Magic bytes formatted xx-xx-xx-xx", "de-ad-be-ef"),
    ("Q4: Multimedia stream SSRC in decimal", "2196231738"),
    ("Q5: Secret string from timing covert channel", "d0nt_ruN_th3_m4lw4r3_y4hh_82117caa"),
    ("Q6: MD5 of reconstructed minidump payload", "c61e123e24a6025bc1aac86391385070"),
    ("Q7: AES Key and IV string", "bd7bf788d62bdec9c219316da4487314_y0u_g0t_tr4pp3d!"),
    ("Q8: Authorization code from CCTV video", "16031115"),
    ("Q9: SHA256 hash of fastloader.exe", "be69c8c00b73aadbb26ca44707ec1d489f891d2e848dd7e834b8f881bcdeb33d"),
    ("Q10: NSIS overlay offset and size", "00009600_046ecd9d"),
    ("Q11: Elevate utility developer name", "Johannes_Passing")
]

def solve():
    print(f"[*] Connecting to {HOST}:{PORT}...")
    s = socket.socket()
    s.settimeout(5)
    s.connect((HOST, PORT))

    def recv_prompt():
        buf = ""
        while True:
            try:
                chunk = s.recv(1024).decode(errors="ignore")
                if not chunk: break
                buf += chunk
                if "Answer:" in buf or ">" in buf or "COMPFEST" in buf:
                    break
            except socket.timeout:
                break
        return buf

    for desc, ans in ANSWERS:
        prompt = recv_prompt()
        print(f"[*] Answering {desc} -> {ans}")
        s.sendall(ans.encode() + b"\n")
        time.sleep(0.3)

    time.sleep(1)
    final_output = ""
    while True:
        try:
            chunk = s.recv(1024).decode(errors="ignore")
            if not chunk: break
            final_output += chunk
        except socket.timeout:
            break

    print("\n" + "="*70)
    print(final_output)
    print("="*70)

    import re
    flag_match = re.search(r"COMPFEST18\{[^}]+\}", final_output)
    if flag_match:
        flag = flag_match.group(0)
        print(f"\n[🏁] FLAG: {flag}")
        return flag

if __name__ == "__main__":
    solve()
