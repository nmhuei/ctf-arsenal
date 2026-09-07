# Writeup: fluxion

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `128` |
| **Author** | `skyv3il` |
| **Solves** | `116` |

---

## 📝 Challenge Overview

Fluxion is a durable workflow engine with a live observability dashboard fronted by Nginx, built on Node.js and Express. Workflows execute asynchronously, pause on internal or external hooks, and stream their run state in real-time.

The core target is an internal privileged workflow:
- `workflowName`: `admin-provision-approval`
- `status`: `awaiting-approval`
- Holds the secret `FLAG` in `run._flag` and an 8-byte hexadecimal `approvalNonce`.

---

## 🔍 Vulnerability & Architectural Analysis

Thorough auditing of the application source code reveals a multi-stage exploit chain combining cryptographic predictability, parser differentials, mass assignment, and template expression injection:

### 1. Insecure PRNG & State Reconstruction (Truncated LCG)
* **Code Location:** `challenge/src/fluxion/src/prng.js`, `challenge/src/fluxion/src/world.js`
* **Mechanism:**
  Step IDs are generated using a 64-bit Linear Congruential Generator:
  $$s_{i+1} = (a \cdot s_i + c) \pmod{2^{64}}$$
  where $a = 6364136223846793005$, $c = 1442695040888963407$.
  The `next()` function emits 24-bit base64url chunks ($s \gg 40$).
  In `world.seed()`, the privileged run generates 5 visible step IDs (`validate-request`, `check-quota`, `reserve-capacity`, `notify-reviewers`, `collect-approvals`) accessible via the RPC method `fetchEvents`.
  Because 5 consecutive 24-bit outputs leak 120 bits of information about the 64-bit state, Babai's Nearest Plane algorithm / LLL lattice reduction uniquely recovers the internal 64-bit seed. Once recovered, advancing the generator by 1 step predicts the 64-bit private `hookToken` emitted by `tz.nextToken()`.

### 2. Authorization Nonce Leakage (Search Prefix Oracle)
* **Code Location:** `challenge/src/fluxion/src/server.js:228-260` (`searchRuns`)
* **Mechanism:**
  The `searchRuns` RPC endpoint allows filtering by indexed fields. For `approvalNonce`, it explicitly permits the `$startsWith` operator:
  ```javascript
  const RESTRICTED = { approvalNonce: ['$startsWith'] };
  ```
  Querying `{ workflowName: 'admin-provision-approval', approvalNonce: { $startsWith: prefix } }` returns `count: 1` when the prefix matches and `0` otherwise. Because `approvalNonce` is a 16-character hex string, testing characters `[0-9a-f]` allows recovering the entire nonce in at most $16 \times 16 = 256$ queries.

### 3. Parser Differential / JSON Key Duplication in Grant Signing
* **Code Location:** `challenge/src/fluxion/src/lib/approvals.js` (`signPreviewGrant`)
* **Mechanism:**
  To resume `admin-provision-approval`, `resumeHook` requires a signed HMAC grant with `aud: "approvals"` and `act: "resume"`.
  The public endpoint `previewApprovalGrant` signs grants, but filters out `"act": "resume"` using regex:
  ```javascript
  const m = raw.match(/"act"\s*:\s*"([^"]*)"/);
  const act = m ? m[1] : '';
  if (BLOCKED_ACTS.has(act)) return { error: '...' };
  ```
  The regex matches only the *first* occurrence of `"act"`. However, when parsed later via native `JSON.parse()`, the *last* duplicate key takes precedence. Sending a document with:
  ```json
  {"act": "preview", "act": "resume", "aud": "approvals", "runId": "<ID>", "nonce": "<NONCE>"}
  ```
  bypasses the regex validation while deserializing into a valid `resume` grant.

### 4. Privilege Escalation via Mass Assignment in Device Enrollment
* **Code Location:** `challenge/src/fluxion/src/rpc/enrollment.js` (`enrollDevice`)
* **Mechanism:**
  Connecting to the binary Fluxion Control Protocol (`POST /fcp`) requires an enrolled device at tier `'operator'`.
  The self-service RPC `enrollDevice` defaults to `tier: 'viewer'`, but performs:
  ```javascript
  const rec = Object.assign(base, profile);
  ```
  Passing `{ profile: { tier: 'operator' } }` overrides the tier and mints a legitimate HMAC-signed operator enrollment token.

### 5. Control-Plane Binary Handshake (FCP)
* **Code Location:** `challenge/src/fluxion/src/lib/fcp.js`
* **Mechanism:**
  With the operator enrollment token and the leaked `approvalNonce`:
  1. `HELLO (0x01)`: Send operator token; server returns `CHALLENGE (0x81)` with `serverSalt`.
  2. `KEX (0x02)`: Derive `sessionKey = HMAC-SHA256(approvalNonce, serverSalt)[0:16]` and send commit MAC over the handshake transcript; server replies `KEXOK (0x82)`.
  3. `TICK (0x04)` / `TOCK (0x84)`: Walk the attestation ladder if required.
  4. `ARM (0x03)`: Send final run confirmation; server returns `ARMED (0x83)` containing the signed `armToken`.

### 6. Prototype Pollution & Scope Error Reflection
* **Code Location:** `challenge/src/fluxion/src/server.js` (`mergeDeep`, `renderRunReport`, `renderCaption`)
* **Mechanism:**
  - `mergeDeep` ignores `'__proto__'` but fails to filter `constructor.prototype`. Calling `saveViewPreferences` with:
    ```json
    {"prefs": {"constructor": {"prototype": {"presentation": {"token": "<approvalNonce>", "caption": "${engine.runs.<adminRunId>._flag}"}}}}}
    ```
    pollutes `Object.prototype.presentation`.
  - Once `resumeHook` is called with the recovered `hookToken`, `grant`, and `armToken`, the run's status changes to `completed`.
  - Calling `renderRunReport` invokes `renderCaption(caption, scope)` where `scope.engine` is `require('./world')`.
  - The path expression resolves to `engine.runs.get("<adminRunId>")._flag` (the flag string).
  - `renderCaption` validates that the scalar value is numeric (`/^-?[0-9]+(\.[0-9]+)?$/`). When it encounters the flag string `TFC{...}`, it throws:
    ```text
    Error: E_SCALAR: 'engine.runs.<runId>._flag' is not a renderable metric: TFC{...}
    ```
  - The catch block in `renderRunReport` captures this exception and reflects the diagnostic message directly in the HTTP JSON response:
    ```json
    {"runId": "<runId>", "report": "render diagnostic", "diagnostic": "Error: E_SCALAR: ... metric: TFC{...}"}
    ```

---

## 💻 Execution Flow & Architecture Summary

```text
[searchRuns ($startsWith)]
         │
         ▼
 Leaked approvalNonce (16 hex chars)
         │
 [fetchEvents] ──> 5 Step IDs (24-bit LCG outputs)
         │
         ├──> [Sage / Babai CVP] ──> Recovered LCG Seed ──> Predicted hookToken
         │
 [enrollDevice] ──> Overwrite tier:'operator' ──> Signed Operator Device Token
         │
 [POST /fcp] ──> Binary Handshake (HELLO -> KEX -> TICK/TOCK -> ARM) ──> Minted armToken
         │
 [previewApprovalGrant] ──> Duplicate JSON key {"act":"preview","act":"resume"} ──> Signed Grant
         │
 [resumeHook] (hookToken + grant + armToken) ──> Status: 'completed'
         │
 [saveViewPreferences] ──> Prototype Pollution (Object.prototype.presentation)
         │
 [renderRunReport] ──> E_SCALAR Exception Reflection ──> FLAG Leaked in Diagnostic
```

---

## 🚩 Flag

- Status: `- [x] Solved / Fully Mapped`
- Flag Pattern: `TFC{...}`
