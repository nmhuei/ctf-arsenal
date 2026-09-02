#!/usr/bin/env python3
import json
import socket

HOST = "socket.cryptohack.org"
PORT = 13415

p = 21888242871839275222246405745257275088696311157297823662689037894645226208583

def recvline(sock):
    data = b""
    while not data.endswith(b"\n"):
        data += sock.recv(1)
    return data.decode()

def send_json(sock, obj):
    sock.sendall((json.dumps(obj) + "\n").encode())

def main():
    s = socket.socket()
    s.connect((HOST, PORT))

    print(recvline(s))

    # Step 1: set z = p-5
    payload = {
        "option": "set_internal_z",
        "z": hex(p - 5)
    }
    send_json(s, payload)
    print(recvline(s))

    # Step 2: trivial proof
    payload = {
        "option": "do_proof",
        "G": "(1,2,1)",
        "hsh": "0x0"
    }
    send_json(s, payload)

    print(recvline(s))

if __name__ == "__main__":
    main()
