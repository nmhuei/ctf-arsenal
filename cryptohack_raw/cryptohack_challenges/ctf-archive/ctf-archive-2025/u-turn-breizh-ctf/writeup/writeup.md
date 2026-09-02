# U-turn (Breizh CTF)

The attachment gives a modular linear relation over a tiny balanced alphabet. The solver recovers the hidden base-5-like digits and reconstructs the final flag block.

Exploit chain:

1. Read `A.txt` and `output.txt` from the challenge attachment.
2. Model the unknown vector `x` with 50 entries constrained to `[-2, -1, 0, 1, 2]`.
3. Add equations `A*x == h mod 256` for every row.
4. Ask Z3 for a satisfying assignment.
5. Interpret the recovered digits as low balanced base-5 digits.
6. Brute force the few missing high digits and keep the candidate whose block XORs with PKCS#7 padding into hex characters.

Run from the extracted challenge directory containing `A.txt` and `output.txt`:

```bash
python3 solve.py
```

Current status: the local Z3 solve did not finish within the short interactive timeout used here, so the flag file is left as unknown instead of guessed.
