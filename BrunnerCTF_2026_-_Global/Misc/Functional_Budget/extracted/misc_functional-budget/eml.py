#!/bin/env python3
import random
import sys

import numpy as np
np.seterr(divide="ignore", over="raise", under="raise", invalid="raise")

# For your recursion pleasure
sys.setrecursionlimit(100_000)


### PARSING CODE, NOT RELEVANT TO THE CHALLENGE ###

TOKENS = ("1", "x", "eml", "(", ")", ",")

def tokenize(expression):
    expression = expression.strip()
    if expression == "":
        return

    for t in TOKENS:
        if expression.startswith(t):
            yield t
            yield from tokenize(expression[len(t):])
            return
    raise Exception("Unexpected charater")

def parse(tokenizer):
    t = next(tokenizer)
    if t in ("1", "x"):
        return t

    if t == "eml":
        assert next(tokenizer) == "("
        x = parse(tokenizer)
        assert next(tokenizer) == ","
        y = parse(tokenizer)
        assert next(tokenizer) == ")"
        return ("eml", x, y)

    raise Exception("Unexpected token")


### CHALLENGE CODE ###

def evaluate(expr, x):
    match expr:
        case "1":
            return np.complex128(1)
        case "x":
            return np.complex128(x)
        case ("eml", lhs, rhs):
            return np.exp(evaluate(lhs, x)) - np.log(evaluate(rhs, x))
        case _:
            raise Exception("Invalid Expression")


print("For each round, enter an expression matching this grammar:")
print("E = 1 | x | eml(E, E)")
print("It must evaluate to the same result as the given equation for all x\n")

ROUNDS = 20
for i in range(ROUNDS):
    print(f"Round {i + 1}/{ROUNDS}")
    a, b = random.randint(-100, 100), random.randint(-100, 100)
    expr = parse(tokenize(input(f"{a}x + {b} = ")))

    # Ensure expression evaluates to expected output for all test inputs
    for _ in range(100):
        x = random.uniform(-10000, 10000)
        evaluated = evaluate(expr, x).real
        if abs(a*x + b - evaluated) > 1e-6:
            print("Wrong")
            exit()

    print("Correct")

print("Congratulations")
print(open("flag.txt").read())
