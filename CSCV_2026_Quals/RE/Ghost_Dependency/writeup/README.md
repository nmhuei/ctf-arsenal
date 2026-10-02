# Writeup: Ghost Dependency

| Property | Value |
| :--- | :--- |
| **Category** | `RE` |
| **Points** | `500` |
| **Author** | `-` |
| **Solves** | `0` |

---

## 📝 Challenge Overview

## Scenario

A Rust warehouse manager agent — valid signature, clean SPDX, green CI. But on exactly one server, the build silently exfiltrates a token. Everything matches when you look at package names. The problem is elsewhere.

Find the component that entered the build, identify the target server, and reproduce the activation condition.

## Provided files

- `warehouse-agent`
- `agent.spdx.json`
- `cargo-build.log`
- `registry.tar.zst`
- `flag.enc`
- `verify.py`
- `FORMAT.md`
- `SHA256SUMS`

## Submission

`verify.py proof.json`


Download [here](https://drive.google.com/file/d/170rHz-PX3XnwdtCSIoB3uBSbKKJXkEXk/view?usp=sharing)

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `RE`
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
