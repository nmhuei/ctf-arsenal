# Writeup: Hackel

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `24` |
| **Author** | `-` |
| **Solves** | `525` |

---

## 📝 Challenge Overview

Our lead cryptographer hackel proudly announced a "revolutionary post-quantum vault" guarded by intricate algebraic group presentations ($S_{11}$ permutation group representations).

```bash
nc 65.109.208.91 3771
```

The service exposes six options:
1. View Public Parameters & Relations
2. View Training Samples & Encrypted Flag Words
3. Homomorphic Word Concatenation Oracle
4. Submit Recovered Equivalent Key (Unlock Flag)
5. Interactive Speed Challenge (Unlock Flag)
6. Exit

---

## 🔍 Reconnaissance & Vulnerability Analysis

Analyzing `hackel.py`:

```python
zero_words = [(t0,) * rng.randint(1, 9) for _ in range(16)]
one_words = [(t0,) * rng.randint(0, 9) + (t1,) for _ in range(16)]
flag_bits = "".join(f"{b:08b}" for b in flag_str.encode("utf-8"))
flag_words = [
    (t0,) * rng.randint(1, 9) if bit == "0" else (t0,) * rng.randint(0, 9) + (t1,)
    for bit in flag_bits
]
```

Where `t0 = 'a'` and `t1 = 'b'`.

### Key Observations:
1. **Plain Generator Encoding**: Despite the elaborate group-theoretic relations and permutations setup, the words encoding bit 0 and bit 1 are never evaluated or rewritten modulo the group relations:
   - A bit `0` is encoded purely as repetitions of symbol `'a'` (e.g., `'a'`, `'aaaa'`).
   - A bit `1` is encoded as 0–9 repetitions of `'a'` followed by symbol `'b'` (e.g., `'b'`, `'aab'`).
2. **Speed Challenge Bypass (Option 5)**:
   - The server provides 16 random challenge words generated with the exact same scheme.
   - If we reply with the 16 bits within 5.0 seconds, the server immediately outputs `[+] FLAG: <flag>`.
   - The classification rule is trivial: `bit = '1' if 'b' in word else '0'`.
3. **Ciphertext Direct Recovery (Option 2)**:
   - Option 2 outputs all `flag_words` directly as text.
   - We can decode the entire flag offline simply by checking whether `'b'` is in each ciphertext word and parsing the 8-bit ASCII chunks.

---

## 💻 Exploitation Strategy & PoC

The exploit script [`../solver/solve.py`](../solver/solve.py) implements both methods:
1. Connect to the service (or local test harness via `--local`).
2. Send option `5` to trigger the interactive speed challenge.
3. Classify the 16 words by checking for generator `'b'`.
4. Receive and store the flag in `flag.txt`.

### Running the Solver

```bash
python3 ../solver/solve.py
```

Local verification output:
```text
[*] Connecting to 127.0.0.1:44045...
[+] Found flag via speed test: ASIS{dummy_flag_for_local_testing_12345}
[+] Flag saved to /home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Hackel/flag.txt
```

---

## 🚩 Flag

- Status: `- [x] Solved`
