#!/usr/local/bin/python3
import os
import socket
import threading
import time

code = """
import sys
def idk(a, b, fn):
    fn(a, b)
code = ''.join(c for c in open("user_input").read() if c in "abcdefghijklmnopqrstuvwxyz:_.[],")
if "ass" in code or "typ" in code or "als" in code:
    print("Nope")
else:
    eval(code, {"__builtins__": {"idk":idk,"sys":sys}})
"""
open("user.py", "w").write(code)

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind(("0.0.0.0", 1234))

def start_user_code_in_thread():
    os.system("python3 user.py")

while True:
    listen_socket.listen(1)
    client_socket, addr = listen_socket.accept()
    client_socket.sendall(b"Send your code:\n")
    with open("user_input", "wb") as f:
        while True:
            data = client_socket.recv(1024)
            if not data or data.strip() == b"END":
                break
            f.write(data)

    client_socket.sendall(b"Running your code...\n")
    thread = threading.Thread(target=start_user_code_in_thread)
    thread.start()
    time.sleep(1)
