# Challenge: NSS CTF (Crypto)

## 1. Challenge Overview & Directory Rules
- Workspace root: `/home/light/Workspace/CTF/NNS_CTF_2026/crypto/NSS_CTF`
- Challenge files:
  - `challenge/crypto_nss-ctf/challenge.sage`
  - `challenge/crypto_nss-ctf/output.py`
- Directory organization:
  - `script/`: Use for draft scripts, tests, and experimentation.
  - `solver/solve.py`: Put the final working solver script here.
  - `writeup/README.md`: Document the solution and flag.
  - `flag.txt`: Save the recovered flag here.
- SageMath executable: `/home/light/.local/bin/sage`

## 2. Cryptographic Scheme: Revised NSS (R-NSS)
The challenge implements R-NSS (Revised NTRU Signature Scheme) over the negacyclic polynomial ring:
$$\mathcal{R} = \mathbb{Z}[x]/(x^{256} + 1)$$
where $n = 256, p = 3, q = 367$.

### Key Generation:
- $u \in \mathcal{T}(90, 91)$ (ternary with 90 ones, 91 minus ones, 75 zeros).
- $f = u + 3 f_1$, where $f_1 \in \mathcal{T}(88, 88)$.
- $g = u + 3 g_1$, where $g_1 \in \mathcal{T}(60, 60)$.
- Coefficients of $f$ and $g$ satisfy $|f_i| \le 4$ and $|g_i| \le 4$.
- $f \equiv g \equiv u \pmod 3$, so $g - f \equiv 0 \pmod 3$.
- Public key $pk = h \equiv g \cdot f^{-1} \pmod{367}$.

### Signing Process:
For each message $m_j \in \mathcal{T}(110, 110)$ ($j = 0, \dots, 9$):
- $y_j = \text{center}(u^{-1} m_j, 3)$
- $z_j \in \mathcal{T}(96, 96)$, $w_j = y_j + 3 z_j$
- $s_j = \text{center}(f \cdot w_j, 367)$
- $t_j = \text{center}(g \cdot w_j, 367)$
- $\text{Dev}_s = \text{center}(s_j - m_j, 3)$, $\text{Dev}_t = \text{center}(t_j - m_j, 3)$
- $e_j[i] = -\text{Dev}_s[i]$ if $\text{Dev}_s[i] == \text{Dev}_t[i]$ else $0$
- $e'_j = \text{center}(u^{-1} e_j, 3)$
- $W_j = w_j + e'_j$
- Output signature: $S_j \equiv f \cdot W_j \pmod{367}$.

### Flag Encryption:
- `key = sha256(bytes(f[i] % 256 for i in range(256))).digest()`
- `ct = AES.new(key, AES.MODE_ECB).encrypt(pad(flag, AES.block_size))`

## 3. Mathematical Cryptanalysis & Attack Strategy
This is the R-NSS scheme analyzed by Craig Gentry & Mike Szydlo in "Cryptanalysis of the Revised NTRU Signature Scheme" (Eurocrypt 2002 / Asiacrypt 2001).

Key relations:
1. $T_j \equiv h \cdot S_j \equiv g \cdot W_j \pmod{367}$.
2. In $\mathbb{Z}[x]/(x^{256} + 1)$, let $A_j = f \cdot W_j$ and $B_j = g \cdot W_j$ be the unreduced polynomial products over $\mathbb{Z}$.
   - The coefficients of $A_j$ and $B_j$ have absolute values $< 350 < \frac{3 \times 367}{2} = 550.5$.
   - $A_j \equiv S_j \pmod{367}$ and $B_j \equiv T_j \pmod{367}$.
   - Modulo 3: $A_j \equiv m_j + e_j \pmod 3$, where $e_j$ is sparse (non-zero on only about 15-25 positions).
   - Because $3 \times 367 = 1101$ and $|A_{j, k}| < 550$, knowing $A_j \pmod{367}$ and $A_j \pmod 3$ uniquely determines $A_j$ over $\mathbb{Z}$ via CRT!
3. Bilinear commutativity over $\mathbb{Z}[x]/(x^{256} + 1)$:
   $$A_i \cdot B_j - A_j \cdot B_i = 0 \quad \text{over } \mathbb{Z}[x]/(x^{256} + 1)$$
   This relation allows identifying and correcting the sparse errors $e_j$ ("Lifting the signatures").
4. Recovering $f$:
   - Once the unreduced $A_j = f \cdot W_j$ are recovered in $\mathbb{Z}[x]/(x^{256} + 1)$, $f$ is the greatest common divisor:
     $$\gcd(A_0, A_1, \dots, A_9) = f$$
     which can be recovered via the ideal GCD lattice (e.g. LLL on the lattice spanned by rotations of $A_j$).
   - Alternatively, use lattice reduction directly on $(f, g)$ relations ($f \cdot h \equiv g \pmod{367}$, $f \equiv g \pmod 3$), or other lattice/correlation methods.

## 4. Tasks Required:
1. Write testing/solver scripts in `script/`.
2. Recover $f(x) \in \mathbb{Z}[x]/(x^{256} + 1)$.
3. Derive the AES key, decrypt `ct`, and obtain the flag `NNS{...}`.
4. Save the final working solver in `solver/solve.py`.
5. Save the flag in `flag.txt` and provide a complete writeup in `writeup/README.md`.
