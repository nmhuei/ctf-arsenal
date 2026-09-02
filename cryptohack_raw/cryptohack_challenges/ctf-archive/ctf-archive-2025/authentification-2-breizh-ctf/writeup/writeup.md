# Authentification 2 (Breizh CTF)

This is the fixed-looking version of Authentification 1, but the custom GCM implementation still leaks enough algebraic structure to recover a valid authentication tag for a forged admin token.

Exploit chain:

1. Create a chosen guest account and capture the AES-GCM cookie.
2. The broken implementation uses the same GCTR block for plaintext encryption and the GHASH mask. From the first known plaintext block, recover the tag mask.
3. Model GHASH over `GF(2^128)` with the challenge bit ordering.
4. Use the known ciphertext/tag pair to form a low-degree polynomial in the GHASH key `H`.
5. Solve for candidate `H` roots in Sage.
6. Encrypt the target JSON `{"username": "", "role": "super_admin"}` with the recovered CTR keystream.
7. Recompute GHASH for the forged ciphertext and submit the forged cookie to `/admin`.

Verified command:

```bash
source /home/light/miniforge3/etc/profile.d/conda.sh
conda activate sage
sage -python solve_authentification2_sage.py http://archive.cryptohack.org:59670
```
