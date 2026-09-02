#!/usr/local/bin/python3
import re

def collatz(num):
    while num != 1:
        yield num
        if num % 2:
            num = num * 3 + 1
        else:
            num = num // 2
    yield 1

code = input("code > ")
gen = collatz(int(input("starting num > "), 0))

if not code.isascii() or len(code) >= 400:
    print("You can't do that")
    exit(1)

for m in re.findall(r"\w+", code):
    try:
        expected_len = next(gen)
    except StopIteration:
        print("You're out of lengths!")
        exit(2)
    
    if len(m) != expected_len:
        print("Length mismatch")
        exit(3)

eval(code, {'__builtins__': {}})
