#!/usr/bin/env python3
"""Solution for Hardware accelerated flag checker 1 (NNS CTF 2026 - misc)

Analyzes the synthesized Verilog gate netlist (`netlist.v`).
The circuit implements a 5-bit FSM (states 0 to 31) where transitions
occur on ASCII characters (7-bit `character` input).
The flag is the unique sequence driving state 0 -> state 31 (found_flag = 1).
"""
import os
import re
from collections import deque

def solve():
    netlist_path = os.path.join(
        os.path.dirname(__file__), "..", "script", "misc_hardware-accelerated-flag-checker-1", "netlist.v"
    )
    if not os.path.exists(netlist_path):
        netlist_path = os.path.join(os.path.dirname(__file__), "netlist.v")

    with open(netlist_path) as f:
        lines = f.readlines()

    assigns = []
    for line in lines:
        line = line.strip()
        m = re.match(r'assign\s+([^=]+)\s*=\s*(.+);', line)
        if m:
            lhs, rhs = m.group(1).strip(), m.group(2).strip()
            assigns.append((lhs, rhs))

    code = ['def step(s_val, char_val):']
    code.append('    reset_n = 1')
    for i in range(5):
        code.append(f'    s_{i} = (s_val >> {i}) & 1')
    for i in range(7):
        code.append(f'    c_{i} = (char_val >> {i}) & 1')

    def tr(expr):
        expr = re.sub(r'character\[(\d+)\]', r'c_\1', expr)
        expr = re.sub(r's\[(\d+)\]', r's_\1', expr)
        while '~' in expr:
            expr = re.sub(r'~([a-zA-Z0-9_]+)', r'(1 ^ \1)', expr)
            expr = re.sub(r'~\(([^()]+)\)', r'(1 ^ (\1))', expr)
        return expr

    for lhs, rhs in assigns:
        var_name = lhs.replace('[', '_').replace(']', '_')
        py_rhs = tr(rhs)
        code.append(f'    {var_name} = ({py_rhs}) & 1')

    code.append('    next_s = (_289__0_) | (_289__1_ << 1) | (_289__2_ << 2) | (_289__3_ << 3) | (_289__4_ << 4)')
    code.append('    flag = found_flag')
    code.append('    return next_s, flag')

    env = {}
    exec('\n'.join(code), env)
    step = env['step']

    # BFS from state 0
    queue = deque([(0, '')])
    visited = {0: ''}

    while queue:
        curr_s, path = queue.popleft()
        if curr_s == 31:
            print(f"FLAG: {path}")
            return path
        for c in range(32, 127):
            ns, _ = step(curr_s, c)
            if ns not in visited:
                visited[ns] = path + chr(c)
                queue.append((ns, path + chr(c)))

if __name__ == '__main__':
    solve()
