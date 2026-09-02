import concurrent.futures
import re
import socket
from pathlib import Path

HOST = "10.112.0.12"
text = Path("redscan.gnmap").read_text()
ports = sorted({int(x) for x in re.findall(r"(\d+)/open/tcp", text)})


def grab(port: int):
    try:
        with socket.create_connection((HOST, port), timeout=1.0) as s:
            s.settimeout(1.0)
            data = s.recv(512)
            return port, data
    except OSError:
        return port, b""

with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
    for port, data in pool.map(grab, ports):
        if b"Red Tide Terminal" in data:
            print(f"MATCH {HOST}:{port} {data!r}")
        elif data:
            print(f"BANNER {HOST}:{port} {data[:120]!r}")
