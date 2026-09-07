Local Program Inventory
Scope

This inventory is limited to files present in the current workspace. It records program structure and observable data flow only. It does not attempt to solve, factor, decrypt, recover secrets, derive hidden coefficients, or construct an attack/solver.

Workspace Files

apbq-rsa-iv.py

Python script.

Executable text file.

Main runnable program in the workspace.

crypto_apbq-rsa-iv.tar.gz

gzip-compressed tar archive.

Contains one file:

crypto_apbq-rsa-iv/apbq-rsa-iv.py

archived size: 3149 bytes

mode: -rwxrwxrwx

owner/group metadata: kona/kona

timestamp: 1970-01-01 08:00

The archived source matches the workspace copy byte-for-byte.

Program Entry Point

The program has no if __name__ == "__main__": wrapper. Execution begins immediately at top level when apbq-rsa-iv.py is run with Python.

Nominal local entry point:

python3 apbq-rsa-iv.py

Imports / Runtime Dependencies

The program imports:

getPrime from Crypto.Util.number

bytes_to_long from Crypto.Util.number

randint from Python's random module

The Crypto.Util.number import implies a local PyCryptodome-compatible Python environment is required to execute the generator.

Inputs
Generated inputs / hidden runtime values

At runtime the program generates:

p = getPrime(1024)

a fresh 1024-bit prime

q = getPrime(1024)

a fresh 1024-bit prime

For each of three hint records it generates:

a = randint(0, 4**312)

b = randint(0, 4**312)

The endpoints are inclusive because Python randint(a, b) includes both endpoints.

Thus each hint coefficient is an integer in:

0 <= a,b <= 4**312

File input

The program reads:

flag.txt

using:

open('flag.txt', 'rb').read().strip()

Properties:

path is relative to the process current working directory

mode is binary

the complete file contents are read

leading/trailing ASCII whitespace bytes handled by bytes.strip() are removed before encryption

the resulting byte string is stored as FLAG

There is no command-line argument parsing, stdin input, socket input, environment-variable input, or network input in the source.

Embedded public instance

A triple-quoted string at the end of the source contains a fixed previously generated public instance consisting of:

n = <large decimal integer>

c = <large decimal integer>

hints = [<three large decimal integers>]

This block is inert string-literal data during normal execution; it is not parsed or assigned by the running program.

Constants

Explicit constants used by the executable code:

prime size: 1024 bits

RSA public exponent:

e = 0x10001

hexadecimal literal, equal to the standard integer public exponent represented by that literal

number of hints: 3

hint coefficient upper-bound expression: 4**312

coefficient lower bound passed to randint: 0

flag filename: 'flag.txt'

flag open mode: 'rb'

The source also contains one fixed embedded public instance in the trailing triple-quoted string.

Arithmetic / Data Flow
RSA modulus construction

The program computes:

n = p * q

using ordinary Python integer multiplication.

Hint construction

For each of three iterations:

sample a

sample b

compute:

a * p

b * q

add them:

a * p + b * q

append the resulting integer to hints

So each generated hint has the direct program form:

h_i = a_i * p + b_i * q

No modular reduction is applied to the hint values by the source.

Flag conversion

The stripped byte string FLAG is converted to a nonnegative integer with:

bytes_to_long(FLAG)

This interprets the bytes as a big-endian integer according to the imported helper's behavior.

Ciphertext computation

The program computes:

c = pow(bytes_to_long(FLAG), e, n)

Python's three-argument pow performs modular exponentiation, producing the ciphertext integer modulo n.

Data Formats
Prime / coefficient / modulus / ciphertext / hints

All arithmetic values are Python arbitrary-precision integers.

Flag

source representation: raw bytes from flag.txt

preprocessing: .strip()

encryption representation: integer produced by bytes_to_long

Hints

hints is a Python list containing exactly three Python integers.

Embedded instance

The embedded instance is written as textual Python-like assignments using base-10 integer literals and a list literal.

Output Behavior

Normal execution emits exactly three print calls:

print(f'{n = }')

print(f'{c = }')

print(f'{hints = }')

Therefore stdout is three textual lines in this general form:

n = <decimal integer>

c = <decimal integer>

hints = [<decimal integer>, <decimal integer>, <decimal integer>]

The program does not explicitly write generated results to a file.

The program does not print:

p

q

individual a_i

individual b_i

raw flag bytes

converted flag integer

Randomness / Repeatability

A fresh run normally changes:

p

q

all six sampled hint coefficients

therefore n

therefore the hint values

normally the ciphertext as well because the modulus changes

The source does not seed Python's random module itself.

getPrime has its own randomness source through the imported cryptographic utility.

Possible Local Test Hooks

These are execution/inspection hooks only; they are not solver steps.

1. Generator smoke test

Create a local flag.txt containing a harmless test value and run:

python3 apbq-rsa-iv.py

This checks that:

dependencies import

primes generate

the flag file is read

three hints are produced

three output lines are printed

It does not require using the embedded public instance.

2. Output-format validation

A local test can verify that stdout contains exactly:

one n = ... line

one c = ... line

one hints = [...] line

and that the parsed hints object has length 3.

3. Freshness check

Running the generator more than once with the same harmless local flag can confirm that generated public values change between independent executions.

4. Archive/source consistency check

The archived Python file can be streamed with tar -xOzf and compared against the workspace source without extracting outside the workspace.

For the inspected workspace, the two copies match byte-for-byte.

5. Static syntax/import check

Local-only checks can include Python syntax compilation or an import/dependency check without modifying the challenge logic.

6. Instrumented educational copy

If later steps explicitly permit it, a separate local copy could add diagnostic prints/assertions for generated internal values. The current source should remain unchanged during this inventory step.

Not Present in the Source

No evidence was found in the inspected program of:

network access

remote service endpoints

HTTP requests

sockets

browser interaction

subprocess execution

package installation

command-line options

stdin parsing

environment-variable configuration

serialization beyond printed Python-style decimal/list text

an implemented decryptor

an implemented solver

Step Boundary

This inventory intentionally stops before arithmetic analysis of the fixed instance. No attempt has been made here to recover p, q, the hidden hint coefficients, plaintext, or any flag.

INVENTORY_COMPLETE
