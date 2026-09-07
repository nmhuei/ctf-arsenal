# Crypto Party 2 Solver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover the live challenge's ECDSA key from six UUID-biased nonces, decrypt the AES-ECB ciphertext, and leave a reproducible solver, flag, and explanation in the challenge workspace.

**Architecture:** Keep the solver self-contained in `solver/solve.py`. It will separate protocol collection, ECDSA/HNP arithmetic, UUID-prefix constraints, lattice reduction, candidate validation, and AES decryption so the cryptanalytic core can be tested entirely offline before one six-query live run. The writeup will explain the nonce construction and the recovery flow without reproducing the full script.

**Tech Stack:** Python 3; `ecdsa` for NIST256p parameters; `fpylll` for integer lattice reduction; PyCryptodome for AES-ECB and PKCS#7 unpadding; Python `ssl` sockets for the TLS service.

**Spec:** User request and `challenge/crypto_crypto-party-2/chall.py`.

## Global Constraints

- Use exactly the challenge's NIST256p order and ECDSA equation.
- The live client must use TLS with `server_hostname` set to the challenge hostname.
- Use no more than the server's six invite queries.
- Do not submit the recovered flag to any CTF platform.
- Reject unvalidated/decoy plaintext and only save a flag after AES unpadding and flag-format validation.

---

### Task 1: Cryptanalytic regression harness

**Files:**
- Create: `solver/test_solve.py`
- Read: `challenge/crypto_crypto-party-2/chall.py`

**Interfaces:**
- The tests will exercise `uuid_prefix_valid`, `nonce_from_uuid_prefix`, `recover_private_key`, and `decrypt_flag` from `solver.solve`.
- Tests generate real NIST256p points and signatures locally, so the recovery test does not depend on the network.

- [ ] **Step 1: Write failing tests**

  Add tests that reject malformed UUID prefixes, reproduce the challenge nonce conversion, recover a synthetic private key from six valid signatures, and decrypt a locally generated AES-ECB ciphertext with PKCS#7 padding.

- [ ] **Step 2: Run the tests and verify the expected missing-implementation failures**

  Run `python -m pytest -q solver/test_solve.py`. Expected: collection or assertion failures because the requested solver interfaces are not implemented yet.

### Task 2: Implement the offline solver core

**Files:**
- Modify: `solver/solve.py`
- Test: `solver/test_solve.py`

**Interfaces:**
- `uuid_prefix_valid(prefix: str) -> bool`
- `nonce_from_uuid_prefix(prefix: str) -> int`
- `recover_private_key(signatures: list[tuple[int, int, bytes]], order: int) -> int`
- `decrypt_flag(ciphertext: int, secret_key: int) -> bytes`

- [ ] **Step 1: Implement the UUID constraint and nonce conversion helpers**

  Enforce the UUIDv4 fixed hyphens/version/variant positions and hexadecimal positions, then convert the first 32 ASCII characters using big-endian integer semantics.

- [ ] **Step 2: Implement the HNP/digit-lattice recovery and candidate checks**

  Transform each signature to `k_i = alpha_i*d + beta_i (mod n)`, encode the constrained ASCII nonce digits in the lattice, reduce with `fpylll`, enumerate plausible reduced/nearest-plane candidates, and accept only a key whose reconstructed nonce bytes satisfy all six UUID constraints and all signature equations.

- [ ] **Step 3: Run the offline tests and a local challenge-style smoke test**

  Run `python -m pytest -q solver/test_solve.py`; expected: all tests pass. Also run a local six-signature generation loop using the exact challenge formula and verify key recovery plus decryption.

### Task 3: TLS collection and live recovery

**Files:**
- Modify: `solver/solve.py`
- Create: `flag.txt`

**Interfaces:**
- The CLI connects to `crypto-party-2-236264a8fb08.chall.nnsc.tf:1337`, parses `ct`, sends six friend names, parses six `r:s` pairs, recovers the key, decrypts, validates the plaintext, and writes only the validated flag to `flag.txt`.

- [ ] **Step 1: Add the TLS protocol client**

  Use `ssl.create_default_context()`, `socket.create_connection`, and `ctx.wrap_socket(..., server_hostname=HOST)`. Read prompts incrementally and make exactly six invite requests.

- [ ] **Step 2: Run the solver once against the live service**

  Run `python solver/solve.py`; verify the process exits successfully and its plaintext passes the flag-format check.

- [ ] **Step 3: Inspect the saved artifact**

  Run `test -s flag.txt` and inspect it as plain text. Do not send it to a platform.

### Task 4: Write the concise methodology

**Files:**
- Modify: `writeup/README.md`

- [ ] **Step 1: Document the vulnerability and equations**

  Explain the UUID prefix's fixed/constrained ASCII bytes, the ECDSA rearrangement, the digit-lattice/CVP strategy, validation, and AES-ECB decryption flow without pasting the complete script.

- [ ] **Step 2: Verify deliverables**

  Run `python -m pytest -q solver/test_solve.py`, `python -m py_compile solver/solve.py`, and `test -s flag.txt`; inspect `git diff -- solver/solve.py writeup/README.md flag.txt`.
