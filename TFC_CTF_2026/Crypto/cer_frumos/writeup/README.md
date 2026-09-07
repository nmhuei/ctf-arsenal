# Writeup: cer frumos

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `50` |
| **Author** | `minipif` |
| **Solves** | `284` |
| **Status** | `Completed` |

---

## 📝 Challenge Overview

The challenge provides a generator script `test.py` and output log `out.txt`. The script initializes Python's `random` PRNG (Mersenne Twister MT19937) with a random seed:

```python
random.seed(random.randint(0, 2**128))
for i in range(625):
    x = random.getrandbits(48)
    random.getrandbits(16)
    print(x)
for i in range(10):
    x = random.getrandbits(32)

key = sha256(str(random.getrandbits(64)).encode()).digest()
nonce = sha256(str(random.getrandbits(64)).encode()).digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv=nonce)
enc_flag = cipher.encrypt(flag)
print(f'Enc flag: {enc_flag.hex()}')
```

We are given 625 48-bit outputs of `getrandbits(48)` along with the hexadecimal ciphertext `enc_flag`.

---

## 🔍 Vulnerability & Mathematical Analysis

Python's `random` module is implemented using the **MT19937 Mersenne Twister** algorithm:
1. **Internal State**: An array of $N = 624$ 32-bit words, totaling $624 \times 32 = 19,968$ bits.
2. **State Transition (Twist)**: When the 624 words are exhausted, a twist operation updates the state. The recurrence relation is:
   $$x_k = x_{k+M} \oplus ((x_k \text{ upper 1 bit}) \mid (x_{k+1} \text{ lower 31 bits})) \cdot A$$
   where $M = 397$ and $A$ is a constant bitmask `0x9908b0df`. All operations in the twist are bit shifts and XORs, making them **linear transformations over $\mathbb{GF}(2)$**.
3. **Tempering (Output Transform)**: When extracting a 32-bit word, a 4-step bitwise XOR/shift sequence is applied:
   $$y_1 = y_0 \oplus (y_0 \gg 11)$$
   $$y_2 = y_1 \oplus ((y_1 \ll 7) \ \& \ \text{0x9D2C5680})$$
   $$y_3 = y_2 \oplus ((y_2 \ll 15) \ \& \ \text{0xEFC60000})$$
   $$y_4 = y_3 \oplus (y_3 \gg 18)$$
   Every single bit in $y_4$ is a linear combination over $\mathbb{GF}(2)$ of the bits of $y_0$.
4. **`random.getrandbits(k)` in CPython**:
   - For $k = 48$: CPython extracts $\lceil 48/32 \rceil = 2$ 32-bit tempered words $(w_0, w_1)$ and constructs:
     $$\text{val} = ((w_1 \ \& \ \text{0xFFFF}) \ll 32) \mid w_0$$
   - For $k = 16$: CPython extracts 1 32-bit tempered word $w_2$, taking $w_2 \ \& \ \text{0xFFFF}$ and discarding the remaining 16 bits.
   - Thus, each iteration of the loop consumes exactly 3 32-bit words ($w_0, w_1, w_2$).

Across 625 iterations:
- Words consumed: $625 \times 3 = 1875$ words (spanning multiple twists).
- Known output bits: $625 \times 48 = 30,000$ bits.

Since each observed bit is a linear equation over the initial 19,968 state bits, we have 30,000 equations for 19,968 unknowns over $\mathbb{GF}(2)$. This is an over-determined linear system:
$$M \cdot \mathbf{s} = \mathbf{b} \pmod 2$$
which has a unique solution.

---

## 🛠️ Recovery & Exploitation Strategy

1. **Symbolic Bit Tracking**:
   - Model the initial state as 624 words $\times$ 32 symbolic basis vectors in $\mathbb{GF}(2)^{19968}$.
   - Implement bitwise linear operations for:
     - In-place MT19937 twisting (`twist_inplace_bits`)
     - Bitwise tempering (`temper_bits`)
2. **Matrix Formulation**:
   - Trace the exact sequence of `getrandbits(48)` and `getrandbits(16)` calls.
   - For each bit of the 48-bit outputs in `out.txt`, add a row to matrix $M$ corresponding to its symbolic expression and append the observed bit to $\mathbf{b}$.
3. **Linear System Solving**:
   - Solve $M \cdot \mathbf{s} = \mathbf{b}$ using SageMath's Gaussian elimination over $\mathbb{GF}(2)$.
4. **State Reconstruction & Decryption**:
   - Rebuild the 624 32-bit integer state array from $\mathbf{s}$.
   - Initialize a Python `random` instance with the reconstructed state.
   - Advance through the 625 iterations of 48-bit and 16-bit calls, followed by the 10 iterations of 32-bit calls.
   - Generate:
     - `key = sha256(str(random.getrandbits(64)).encode()).digest()`
     - `nonce = sha256(str(random.getrandbits(64)).encode()).digest()[:16]`
   - Decrypt `enc_flag` via AES-CBC (`iv=nonce`) and unpad to recover the flag.

---

## 💻 Solver Implementation

The solver [`../solver/solve.py`](../solver/solve.py):

```python
#!/home/light/miniforge3/envs/sage/bin/python
import os, sys, random
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sage.all import GF, matrix, vector

# 1. Tempering & Twist over GF(2)
def temper_bits(w): ...
def twist_inplace_bits(mt): ...

# 2. Build linear system M * s = b
# 3. Solve for initial state s
# 4. Fast-forward PRNG state and decrypt flag
```

Running the solver:
```bash
python3 ../solver/solve.py
```

Output:
```
[+] Solving linear system of size 19968 over GF(2)...
[+] State reconstructed successfully!
[+] Decrypted Flag: TFCCTF{ursu_ursa_bea_ursus_intrun_urus_verzuliu}
```

---

## 🚩 Flag

```
TFCCTF{ursu_ursa_bea_ursus_intrun_urus_verzuliu}
```
