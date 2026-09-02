#!/usr/bin/env python3

import socket
import ssl
import time

HOST = "transcendent-renovation.instances.ctf.l3ak.team"
PORT = 1337

# Mở rộng brute force cho Q7
CANDIDATES = [
    # Possibly needs different folders from other streams
    "New folder",
    "Ghosts",
    "Artificial Intelligence",
    "The Intelligence",
    "Voices",
    "L3AK",
    "NoNeedToWonder",
    # Maybe full path
    r"C:\Users\Administrator\Desktop\New folder",
    r"C:\Users\Administrator\Desktop\Ghosts",
    r"C:\Users\Administrator\Desktop\Artificial Intelligence",
    # Maybe HauntedHouse related
    "HauntedHouse",
    "Haunted House",
]


def connect():
    context = ssl._create_unverified_context()
    raw_socket = socket.create_connection((HOST, PORT), timeout=15)
    sock = context.wrap_socket(raw_socket, server_hostname=HOST)
    sock.settimeout(3)
    return sock


def recv_until(sock, marker: bytes, timeout: float = 10) -> bytes:
    data = b""
    end_time = time.time() + timeout
    while marker not in data and time.time() < end_time:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            continue
    return data


def recv_remaining(sock, timeout: float = 3) -> bytes:
    data = b""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            end_time = time.time() + 0.5
        except socket.timeout:
            break
    return data


def main():
    for idx, answer in enumerate(CANDIDATES, 1):
        print("=" * 70)
        print(f"[{idx}/{len(CANDIDATES)}] Trying Q7: {answer!r}")

        sock = connect()
        try:
            banner = recv_until(sock, b"Enter question number to answer:")
            sock.sendall(b"7\n")
            question = recv_until(sock, b"Enter your answer:")
            print(f"  Sending: {answer}")
            sock.sendall(answer.encode() + b"\n")
            result = recv_remaining(sock, timeout=5)
            text = result.decode(errors="replace")

            if "Incorrect" in text or "✖" in text:
                print(f"  ✖ WRONG")
            else:
                print(f"  ✔ CORRECT!")
                print(text)
                return

        except Exception as e:
            print(f"  [ERROR] {e}")
        finally:
            sock.close()

        time.sleep(0.5)

    print("\n[-] None of the candidates worked.")


if __name__ == "__main__":
    main()
