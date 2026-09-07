# The Builder Solution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a self-contained solver that exploits The Builder service, extracts the flag without submitting it, and records the technical method.

**Architecture:** Reconnaissance will identify the web API, generated build configuration, registry behavior, and the exact secret/image-layer leak. The solver will use Python's standard library HTTP client, keep the attack sequence deterministic, print the discovered flag, and write it to the challenge root's `flag.txt`; a small test will cover request construction and flag extraction without requiring the live target.

**Tech Stack:** Python 3 standard library, HTTPS/HTTP APIs, Docker Registry HTTP API, pytest.

**Spec:** User request and live target behavior supplied in the conversation.

## Global Constraints

- Do not submit the flag to any platform or submission endpoint.
- Keep exploratory scripts and payloads under `script/`.
- The official exploit must be `solver/solve.py`.
- The final flag must be saved to `flag.txt` and the methodology to `writeup/README.md`.

### Task 1: Recon the web application and registry

**Files:**
- Read: `challenge/README.md`, `metadata.json`
- Create: `script/recon.py` only if reusable probing is needed
- Test: live HTTPS requests to the two supplied hosts

**Interfaces:**
- Consumes: the two target hostnames from the user request.
- Produces: observed routes, request schemas, build identifiers, registry repositories/manifests, and the secret exposure primitive needed by the solver.

- [x] **Step 1:** Fetch the web root and inspect status, headers, HTML, JavaScript, and robots metadata.
- [x] **Step 2:** Enumerate API routes and infer request fields from frontend assets and error responses.
- [x] **Step 3:** Submit harmless static-site builds and record generated image names, logs, configuration, and registry responses.
- [x] **Step 4:** Trace where build secrets enter the generated configuration and which registry layer/blob exposes them.

### Task 2: Add a failing solver-behavior test

**Files:**
- Create: `tests/test_solver.py`
- Read: `solver/solve.py`

**Interfaces:**
- Consumes: pure helper functions exposed by `solver.solve`, with no live network dependency.
- Produces: assertions for the discovered exploit request sequence and extraction of a `FLAG{...}` value from the service response/blob.

- [x] **Step 1:** Write tests for URL joining, registry manifest/blob parsing, and flag extraction based on the observed response format.
- [x] **Step 2:** Run `pytest -q tests/test_solver.py` and confirm failure because the required helpers are not implemented.

### Task 3: Implement the exploit solver

**Files:**
- Modify: `solver/solve.py`

**Interfaces:**
- Consumes: target URLs from constants or `WEB_URL`/`REGISTRY_URL` environment overrides.
- Produces: `solve()` that executes the build-to-registry exploit and writes the first discovered flag to `flag.txt`; pure parsing helpers used by the tests.

- [x] **Step 1:** Implement the smallest HTTP helpers needed for JSON and registry requests, with TLS verification disabled only as needed for the challenge certificate.
- [x] **Step 2:** Implement the exact build request and follow-up registry/config/blob requests identified during reconnaissance.
- [x] **Step 3:** Parse all relevant text safely for the flag, fail loudly if none is found, and write only the flag plus a newline to `flag.txt`.
- [x] **Step 4:** Run the unit test and verify it passes.

### Task 4: Retrieve and verify the flag

**Files:**
- Create/modify: `flag.txt`
- Read: `solver/solve.py`

**Interfaces:**
- Consumes: live target endpoints and the completed solver.
- Produces: a locally saved flag; no platform submission request.

- [x] **Step 1:** Run `python3 solver/solve.py` against the supplied endpoints.
- [x] **Step 2:** Confirm the output matches the CTF flag format and `flag.txt` contains the same value.
- [x] **Step 3:** Inspect the command/request code to confirm no submission endpoint is called.

### Task 5: Document the methodology

**Files:**
- Modify: `writeup/README.md`

**Interfaces:**
- Consumes: the verified request sequence and vulnerability explanation.
- Produces: a concise technical writeup covering reconnaissance, root cause, exploit chain, and local execution.

- [x] **Step 1:** Replace placeholders with the actual endpoints, API flow, vulnerable build/configuration behavior, registry extraction, and flag status.
- [x] **Step 2:** Run a final repository diff/status check and repeat unit plus live solver verification.
