# Do you have good eyes? (Breizh CTF)

The service repeatedly asks whether a sanitized MLWE-looking sample is real or random. The solver projects the polynomial instance at `X = 1`, reducing the module-LWE instance to a small integer lattice problem.

Exploit idea:

1. Decode the sanitized matrix/vector from the gzip+base64 Python literal format.
2. Evaluate every polynomial at `X = 1` modulo `q`.
3. For real MLWE samples, `t = A*s + e` with small secret/error, so `(s, A*s + q*c)` lies close to `(0, t)`.
4. Build the lattice with rows for the secret coordinates and modulus rows.
5. Run LLL and Babai nearest-plane; a small residual distinguishes MLWE from random.
6. Repeat for all service rounds and send `1` for MLWE, `0` for random.

Current status: the copied solver is the working analysis artifact, but the remote run in this session timed out before the final flag. Retry with a longer timeout or a more stable network connection:

```bash
python3 local_eyes_solver.py --remote archive.cryptohack.org 43607
```
