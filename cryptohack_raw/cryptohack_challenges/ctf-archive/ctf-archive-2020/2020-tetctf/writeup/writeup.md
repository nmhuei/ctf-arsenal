# 2020 (TETCTF)

The service asks for the 2020th output of a Mersenne-Twister-like PRNG after leaking two chosen indexed outputs. The solver uses MT tempering inversion and the twist relation.

Exploit chain:

1. Request outputs at indices 1396 and 1792.
2. Untemper both outputs to recover internal state words.
3. Use the MT twist recurrence to derive two possible candidates for state/output index 2019.
4. Submit one candidate; if the ambiguous high bit was wrong, reconnect and submit the other.
5. The service prints the flag.

Verified command:

```bash
python3 solve.py archive.cryptohack.org 63222
```
