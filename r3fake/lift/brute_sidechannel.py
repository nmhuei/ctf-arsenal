#!/usr/bin/env python3
"""
Brute-force the flag character by character using dispatch call count
as a side channel. Each indirect call at 0x21425d is a dispatch operation.
More operations = further in validation = more correct characters.
"""

import subprocess
import sys
import time

BINARY_PATH = '/home/light/Workspace/CTF/r3fake/lift/chall'
FLAG_LEN = 39
CONTENT_LEN = 32

ASSERT_CHARSET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!@#$%^&*()-+=[]{}|;:,.<>?/~` '

def count_dispatches(flag_content):
    """
    Run binary with given flag and count how many times the dispatch
    indirect call at 0x21425d is hit before exit.
    """
    flag = f"R3CTF{{{flag_content}}}"
    gdb_script = f"""
set pagination off
set disable-randomization on
file {BINARY_PATH}
break *0x555555554000 + 0x21425d
commands
  silent
  set $count = $count + 1
  continue
end
run <<< "{flag}"
quit
"""
    try:
        result = subprocess.run(
            ['gdb', '-q', '-batch', '-ex', gdb_script],
            input=flag + '\n',
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Parse the count from the output
        output = result.stdout + result.stderr
        if 'Correct' in output:
            print(f"CORRECT FLAG FOUND: {flag}")
            return flag
        # Count "Breakpoint" occurrences in output
        count = output.count('Breakpoint')
        return count
    except subprocess.TimeoutExpired:
        return -1
    except Exception as e:
        return -1


def brute_force_byte(known_content, position):
    """Brute-force one byte position."""
    best_count = 0
    best_char = None

    print(f"\nTrying position {position} (current: {known_content})")

    for c in ASSERT_CHARSET:
        test_content = known_content + c + 'A' * (CONTENT_LEN - len(known_content) - 1)
        count = count_dispatches(test_content)
        if isinstance(flag := count, str):
            return flag  # Full flag found
        if count > best_count:
            best_count = count
            best_char = c
            print(f"  New best: '{c}' -> {count}")

    if best_char:
        print(f"  -> Position {position} = '{best_char}' (count={best_count})")
    return best_char


def main():
    print(f"Starting brute-force side-channel attack on flag content")
    print(f"Using dispatch call count at 0x21425d as oracle")
    print(f"Charset: {ASSERT_CHARSET}")
    print(f"{'='*60}")

    flag_content = "A" * 32
    count = count_dispatches(flag_content)
    print(f"Baseline flag (all A's): {count}")

    # Brute-force one char at a time
    known = ""
    for pos in range(CONTENT_LEN):
        result = brute_force_byte(known, pos)
        if isinstance(result, str):
            print(f"\n{'='*60}")
            print(f"FLAG: {result}")
            print(f"{'='*60}")
            return result
        known += result

    flag = f"R3CTF{{{known}}}"
    print(f"\n{'='*60}")
    print(f"FLAG: {flag}")
    print(f"{'='*60}")
    return flag


if __name__ == '__main__':
    result = main()
    if result:
        print(f"\nFinal flag: {result}")
