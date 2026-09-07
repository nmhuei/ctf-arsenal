# Downhill Solver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover `f` from 500 live NTRUSign signatures and decrypt the Downhill flag.

**Architecture:** `solver/solve.py` will contain protocol handling, ring/convolution helpers, recovery routines, and AES validation in one reproducible standalone script. It will collect signatures once, try exact/statistical/lattice candidate paths, and only accept a candidate that has the challenge’s 73-one binary form and reproduces the public key.

**Tech Stack:** Python 3, TLS sockets, NumPy/SciPy, SageMath subprocess/runtime for exact cyclic polynomial arithmetic when needed, `flatter`, and PyCryptodome.

**Spec:** `docs/superpowers/specs/2026-09-05-downhill-solver-design.md`

## Global Constraints

- Use TLS with `server_hostname='downhill-44905d985cc1.chall.nnsc.tf'`.
- Query no more than the server’s `n_sigs = 500` signatures.
- Do not submit the recovered flag to any CTF platform.
- Preserve the existing unrelated worktree changes.
- Save the recovered flag in `flag.txt` and update `writeup/README.md`.

---

### Task 1: Establish tested algebra and candidate validation helpers

**Files:**
- Modify: `solver/solve.py`
- Test: `solver/solve.py --self-test`

**Interfaces:**
- Produces `cyclic_convolve`, `is_binary_sparse_f`, `derive_key`, and `decrypt_flag` helpers used by later tasks.

- [ ] **Step 1: Add self-tests that initially fail for missing helpers.**

```bash
python3 solver/solve.py --self-test
```

Expected initial result: failure because the helper implementation is absent.

- [ ] **Step 2: Implement minimal cyclic convolution, binary-shape validation, AES derivation, and decrypt/unpad helpers.**

- [ ] **Step 3: Run the self-tests and confirm they pass.**

```bash
python3 solver/solve.py --self-test
```

Expected result: exit 0 and a concise self-test success line.

### Task 2: Implement TLS collection and exact output parsing

**Files:**
- Modify: `solver/solve.py`

**Interfaces:**
- Produces `collect_instance(host, port, count=500) -> (pk, ct, signatures, messages)`.

- [ ] **Step 1: Add parser tests to the self-test for representative `pk`, `ct`, prompt, and signature lines.**
- [ ] **Step 2: Implement a hostname-verified TLS client, timeouts, line buffering, and exactly 500 message/signature exchanges.**
- [ ] **Step 3: Run the parser/self-test before connecting remotely.**

```bash
python3 solver/solve.py --self-test
```

Expected result: exit 0.

### Task 3: Implement hybrid recovery and candidate verification

**Files:**
- Modify: `solver/solve.py`

**Interfaces:**
- Produces `recover_f(pk, messages, signatures) -> list[int]`.

- [ ] **Step 1: Add an offline synthetic smoke test for the candidate filters and signature geometry path.**
- [ ] **Step 2: Implement centering/second-moment estimation, cyclic lattice construction, `flatter`/Sage reduction where available, and candidate enumeration around the recovered short directions.**
- [ ] **Step 3: Implement exact public-key validation and reject candidates that are not 73-one binary polynomials.**
- [ ] **Step 4: Run the offline smoke test and inspect candidate diagnostics.**

```bash
python3 solver/solve.py --self-test
```

Expected result: exit 0.

### Task 4: Run live solve and produce artifacts

**Files:**
- Modify: `solver/solve.py`
- Modify: `writeup/README.md`
- Create: `flag.txt`

- [ ] **Step 1: Run the standalone solver against the supplied TLS endpoint.**

```bash
python3 solver/solve.py
```

- [ ] **Step 2: Verify the recovered `f`, AES plaintext, and flag file independently.**
- [ ] **Step 3: Replace speculative writeup text with the verified attack flow and results, without copying the entire script.**
- [ ] **Step 4: Run all self-tests and a final artifact/status check.**

```bash
python3 solver/solve.py --self-test
test -s flag.txt
git diff -- solver/solve.py writeup/README.md flag.txt
```
