#!/usr/bin/env python3
import socket

def solve():
    HOST, PORT = '65.109.208.91', 3771
    print(f'Connecting to {HOST}:{PORT}...')
    s = socket.create_connection((HOST, PORT), timeout=10)
    f = s.makefile('rw', encoding='utf-8')

    while True:
        line = f.readline()
        if '---------------------------------------------------' in line:
            break

    f.write('5
')
    f.flush()

    flag = None
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        if 'Challenge Words:' in line:
            words = line.replace('Challenge Words:', '').strip().split()
            ans = ''.join('1' if 'b' in w else '0' for w in words)
            f.write(ans + '
')
            f.flush()
        if 'FLAG:' in line:
            flag = line.split('FLAG:')[1].strip()
            print(f'[+] Solved! Flag: {flag}')
            break
    return flag

if __name__ == '__main__':
    solve()
