#!/usr/bin/env python3
"""Solve PoW, get session info, save to JSON"""
import socket
import ssl
import hashlib
import json
import sys
import re
import os

HOST = 'open-world-0e2bbd5fa613.instancer.sekai.team'
PORT = 1337

def solve_pow(prefix, difficulty):
    target = '0' * (difficulty * 2)
    nonce = 0
    while True:
        input_str = str(nonce)
        h = hashlib.sha256((prefix + input_str).encode()).hexdigest()
        if h.startswith(target):
            print(f'[PoW] Found: {input_str} (hash: {h[:16]}...)', file=sys.stderr)
            return input_str
        nonce += 1
        if nonce % 500000 == 0:
            print(f'[PoW] Tried {nonce}...', file=sys.stderr)

def get_session():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    sock = socket.create_connection((HOST, PORT), timeout=30)
    ssock = ctx.wrap_socket(sock, server_hostname=HOST)
    ssock.settimeout(30)

    buffer = b''

    # Read welcome
    while b'action?' not in buffer:
        chunk = ssock.recv(4096)
        if not chunk:
            break
        buffer += chunk
        print(f'[NC] {chunk.decode(errors="replace")!r}', file=sys.stderr)

    # Send 1
    print('[NC] Sending: 1', file=sys.stderr)
    ssock.send(b'1\n')

    # Read PoW challenge
    buffer = b''
    while b'YOUR_INPUT = ' not in buffer:
        chunk = ssock.recv(4096)
        if not chunk:
            break
        buffer += chunk
    print(f'[NC] {buffer.decode(errors="replace")!r}', file=sys.stderr)

    # Parse PoW
    text = buffer.decode()
    m = re.search(r'sha256\("([^"]+)"\s*\+\s*YOUR_INPUT\)', text)
    if not m:
        raise Exception('Could not parse PoW challenge')

    prefix = m.group(1)
    d = re.search(r'must start with (\d+) bytes zeros', text)
    difficulty = int(d.group(1)) if d else 3

    # Solve PoW
    solution = solve_pow(prefix, difficulty)
    print(f'[NC] Sending: {solution}', file=sys.stderr)
    ssock.send((solution + '\n').encode())

    # Read session
    buffer = b''
    while b'seed:' not in buffer:
        chunk = ssock.recv(4096)
        if not chunk:
            break
        buffer += chunk
    print(f'[NC] Session received', file=sys.stderr)

    text = buffer.decode(errors='replace')
    print(text, file=sys.stderr)

    # Parse session
    session = {}
    for line in text.split('\n'):
        if 'uuid:' in line:
            session['uuid'] = line.split('uuid:')[1].strip()
        if 'challenge contract:' in line:
            session['challenge'] = line.split('challenge contract:')[1].strip()
        if 'api v2:' in line:
            session['api'] = line.split('api v2:')[1].strip()
        if 'your wallet version:' in line:
            session['wallet_version'] = line.split('your wallet version:')[1].strip()
        if 'your wallet id:' in line:
            session['wallet_id'] = int(line.split('your wallet id:')[1].strip())
        if 'seed:' in line:
            session['seed'] = line.split('seed:')[1].strip()

    ssock.close()
    return session

if __name__ == '__main__':
    session = get_session()
    print(json.dumps(session))
