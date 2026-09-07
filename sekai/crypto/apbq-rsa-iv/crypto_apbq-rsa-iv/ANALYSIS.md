# apbq-rsa-iv - Static Analysis (Step 1/4)

## Workspace inventory

The current workspace contains exactly one challenge source file:

- apbq-rsa-iv.py - Python source, 3149 bytes.

No archives, binaries, auxiliary source files, or flag.txt are present in the workspace.

## Program entry point

There is no function wrapper or if __name__ == \"__main__\" guard. The module body itself is the program entry point and executes top-to-bottom when run with Python.

Dependencies:

- Crypto.Util.number.getPrime
- Crypto.Util.number.bytes_to_long
- random.randint

## Inputs

The program has no command-line arguments, stdin input, network input, or environment-variable input.

Its only file input is:

- flag.txt, opened in binary mode with open(\"flag.txt\", \"rb\"), then .read().strip().

flag.txt is not included in the current workspace, so the generator cannot be rerun unchanged here without supplying a local test file.

Random secret values generated at runtime are:

- p = getPrime(1024)
- q = getPrime(1024)
- For each of three hints, a and b are sampled independently with randint(0, 4**312).

Because randint is inclusive, each coefficient lies in [0, 4**312] = [0, 2**624].

## Constants and public values

Fixed exponent:

- e = 0x10001 = 65537

RSA modulus construction:

- n = p * q

Hint count:

- exactly 3 linear hints.

The source also contains a triple-quoted literal holding one concrete public challenge instance with values for:

- n
- c
- hints (three integers)

That block is inert data; it is not executed by Python.

## Arithmetic operations

The core arithmetic is:

1. Generate two independent 1024-bit primes p and q.
2. Compute RSA modulus n = p*q.
3. For each of three samples, compute a linear form

 h_i = a_i*p + b_i*q

 where a_i,b_i are at most 624 bits.
4. Convert the stripped flag bytes to a nonnegative integer using bytes_to_long(FLAG).
5. Encrypt with textbook RSA:

 c = m^e mod n

 implemented as pow(bytes_to_long(FLAG), e, n).

There is no padding, hashing, encoding wrapper, signature operation, CRT operation, or additional modular arithmetic in the challenge generator.

## Output format

The program prints three Python-style assignment lines using f-strings:

- n = <decimal integer>
- c = <decimal integer>
- hints = [<decimal integer>, <decimal integer>, <decimal integer>]

The embedded sample block follows exactly this format.

## Local verification path

There is no dedicated checker or verifier script in the workspace.

Two local verification routes are apparent from the source:

1. Generator-level verification: provide a local flag.txt test value and run apbq-rsa-iv.py; it will generate fresh primes, fresh hint coefficients, and print a complete public instance. Because p, q, a, and b are not printed, this confirms generation/output behavior but does not by itself expose the hidden internals for an independent equality check.
2. Static/public-instance verification: the embedded triple-quoted block provides the exact published n, c, and three hints, so later analysis can operate entirely on those public values without needing flag.txt or external access.

No remote service, socket endpoint, URL, or other external system is referenced by the source.

## Scope boundary for step 1

This document intentionally stops at structural inspection. It does not derive p or q, recover any hint coefficients, decrypt c, infer the flag, construct a lattice, or create a solver.
