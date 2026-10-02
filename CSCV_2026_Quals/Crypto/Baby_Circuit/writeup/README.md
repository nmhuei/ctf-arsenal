# Writeup: Baby Circuit

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

While learning zero-knowledge proofs, a student vibe-coded a PLONK prover with an AI and wired it into a hardware accelerator you can tune. It builds, the tests are green, every proof verifies. But does any of it actually run correctly?

The device holds a master key and will only ever tell you one scalar hash and a proof. You get the source of the prover, the verifier and the network launcher; only the device's witness builder ships as a compiled module.

Recover the master key and decrypt the flag.

Download [here](https://drive.google.com/file/d/1iqD4dcc5qrTG2sxB2byi8G02Mmcd42QC/view?usp=sharing)

Connect: `nc 113.20.103.55 1337`

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Crypto`
- Key observations & vulnerability hypothesis:
  *(Document reverse engineering, source code review, or protocol analysis here)*

---

## 💻 Exploitation Strategy & PoC

Exploit script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [ ] Solved`
- Flag: `FLAG{...}`
