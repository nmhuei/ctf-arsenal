# Writeup: Let's Prove It Again

- **Category:** ZKP (Zero-Knowledge Proofs)
- **Platform:** CryptoHack
- **Points:** 300
- **Status:** Solved by `gpt` autonomous agent
- **Flag:** `crypto{CRT_1s_m4gic_for_cryptanalysis}`

---

## 1. Challenge Overview

The challenge presents a remote Fiat-Shamir proof of knowledge protocol for the secret `FLAG` over an unknown prime $p$:
- Group generator $g = 2$.
- $v$ is chosen once per connection: `self.v = self.R.getrandbits(BITS >> 1)` ($512$ bits).
- $FLAG$ is XORed with a $31$-byte nonce: `self.nonce = os.urandom(31)` (revealed in the banner).
- In each round:
  - $p = \text{getPrime}(BITS)$ where $BITS = 1024$.
  - $y = g^{FLAG} \pmod p$.
  - $t = g^v \pmod p$.
  - $c = \text{SHA3-256}(t \oplus y \oplus g \oplus \text{randint}(2, BITS))$.
  - $r = (v - c \cdot FLAG) \pmod{p - 1}$.
  - Server returns $(t, r)$ and $(g, y)$.

---

## 2. Vulnerabilities & Exploitation

1. **Deterministic PRNG Re-seeding via `refresh`**:
   - When `your_turn >= 2`, the client can call `refresh(seed)`.
   - The server sets `self.R = random.Random(self.nonce + seed)`.
   - Because `self.nonce` is known from the connection banner and `seed` is chosen by us, the prime $p$ generated in the subsequent round is completely deterministic and predictable locally!

2. **Elimination of Secret $v$ across Known Moduli**:
   - By interleaving `get_proof` and `refresh`:
     - Proof 1 generated with known $p_1$ (from `seedA`).
     - Proof 3 generated with known $p_3$ (from `seedB`).
   - For each proof, the challenge $c \in \{\text{SHA3-256}(t \oplus y \oplus g \oplus z) : 2 \le z \le 1024\}$ is uniquely determined by testing $t \equiv g^r y^c \pmod p$.
   - Since $v < 2^{512}$ and $c \cdot FLAG < 2^{568} \ll p - 1 \approx 2^{1024}$, the value $v - c \cdot FLAG < 0$ and:
     $$r = (p - 1) + v - c \cdot FLAG$$
     $$\implies v = r - (p - 1) + c \cdot FLAG$$
   - Equating $v$ between Proof 1 and Proof 3:
     $$r_1 - (p_1 - 1) + c_1 \cdot FLAG = r_3 - (p_3 - 1) + c_3 \cdot FLAG$$
     $$\implies FLAG = \frac{(r_3 - p_3 + 1) - (r_1 - p_1 + 1)}{c_1 - c_3}$$
   - This exact integer division recovers $FLAG$ without any modular inversion or ambiguity.

3. **Reversing Nonce XOR**:
   - Undo the 31-byte nonce XOR and discard the random non-printable padding byte to recover the flag string.

---

## 3. Flag
`crypto{CRT_1s_m4gic_for_cryptanalysis}`
