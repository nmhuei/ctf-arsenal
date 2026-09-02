# Writeup: CIA - What does 'I' stand for?

- **Category:** Crypto
- **Difficulty:** Medium
- **Flag:** `PTITCTF{y0Ur_3ff0r7_15_h16hlY_4ppr3c1473D}`

---

## 1. Overview & Analysis

The challenge remote server serves a download link for `chall.py` and `chall.zip`.

Inspecting `chall.py`, we observe the mechanism protecting the zip archive:
- The zip password is generated (64 hex characters from SHA256 digest or 32 hex characters from random token).
- The password is split into $k$ chunks (in `chall.py`, $k = 4$, so 16 characters each; in subsequent nested archives, $k = 1$).
- Each chunk is encrypted using RSA with `PRIME_BITS = 140` ($p, q$ are 140-bit primes, giving a 280-bit modulus $N = p \times q$).
- The public RSA parameters $(N, e, c)$ are given as `PUBLIC_SEGMENTS`.

Because 280 bits ($\approx 84$ decimal digits) is well within the reach of integer factorization algorithms such as **SIQS** (Self-Initializing Quadratic Sieve) or **ECM** (Lenstra's Elliptic Curve Factorization), we can factor each modulus $N$ to retrieve $p$ and $q$, compute the private key $d \equiv e^{-1} \pmod{\phi(N)}$, and decrypt each chunk of the password.

---

## 2. Exploitation Walkthrough

### Step 1: Unzipping `chall.zip`
- Factoring the 4 segments in `chall.py` with YAFU (SIQS with 12 threads):
  - **Segment 0**: `5e2344bd85c76309`
  - **Segment 1**: `6ace28297056f126`
  - **Segment 2**: `434e9768b4435c27`
  - **Segment 3**: `3ec88d447b520d1a`
- Full password: `5e2344bd85c763096ace28297056f126434e9768b4435c273ec88d447b520d1a`
- Extracting `chall.zip` yields `secret.py`, `secret.zip`, and auxiliary challenges (`chall1.py` through `chall10.py`).

### Step 2: Unzipping `secret.zip`
- `secret.py` contains 1 segment ($N$ is 280-bit):
  - $N = 632109254185832433633039421174535485673988540665728059077950081956564713066177228491$
  - Factorization: $p = 728408667178534575163930105969563396254003$, $q = 867794800732239307024667368562103945663497$
  - Decrypted password: `7256f58a379de93bb9ebe176d87d5cf4`
- Extracting `secret.zip` yields `flag.py` and `flag.zip`.

### Step 3: Unzipping `flag.zip` & Retrieving Flag
- `flag.py` contains 1 segment ($N$ is 280-bit):
  - $N = 896949230945185690784357873607286096026939890506455813174654286411035237740830823033$
  - Factorization: $p = 897117007955125283417310768457771208293463$, $q = 999812982020793451491708140725915902633391$
  - Decrypted password: `4664d5e9f13fce5ecfb5a3151c4ba93d`
- Extracting `flag.zip` yields `flag.txt`:
  ```
  PTITCTF{y0Ur_3ff0r7_15_h16hlY_4ppr3c1473D}
  ```

---

## 3. Flag

```
PTITCTF{y0Ur_3ff0r7_15_h16hlY_4ppr3c1473D}
```
