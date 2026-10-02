# Residuegate local analysis

## Evidence

- `metadata.json` and `challenge/NOTE.md` were read first.
- `challenge/here` is a gzip archive containing `give_to_player/`.
- The local service is `local-server/residuegate-hard`, a stripped Rust/axum ELF.
- `qwen_cache.bin` has magic `RGQWEN1\0`, then one 736-byte entry:
  - 32-byte badge commitment
  - 16 records of `32 opaque bytes || 12 signed int8 embedding coordinates`
- The live local router was discovered from a heap dump of the local process:
  - `POST /feature_fa8688cbfa3fc935ae60de224a972126` (session creation)
  - `GET /feature_a9e63777c9a2409902b702d5238a61b8`
  - `POST /feature_11edaf0d1c4e447615614810348a3030`
  - `POST /feature_c26f994e7f7d755a4602972a35430050`
  - `GET /feature_c426f4d0ed166214ae89992cbd592932`

## Model

For each cached variant, the 12-byte quantized embedding is scored with:

`logits = head_weight * embedding + head_bias`

The local metadata sets `required_margin = 12`. The only variant whose top class is the alternate gate class `3` with enough margin is variant `6`, with logits `[76, -75, 156, 168]` and margin `12`.

## Local flag

The local deployment sets:

`FLAG="CTF{local_test_only}"`

The same flag was also visible in the running local process memory after starting the service with the supplied compose environment.

## Evidence audit — 2026-09-25

- Status: UNSOLVED. `flag.txt` is REJECTED as a challenge flag: its value exactly matches the supplied Docker Compose test placeholder. Existing files are retained as historical evidence.
- The previous `worker-report.json` incorrectly marked artifact inspection as `passed`. It has been corrected to `not_verified` / `unsolved`; no successful completion of the challenge verifier is established.
- Static review of `solver/solve.py` confirms it scores cache entries and reads a test flag from process memory or Compose; it does not solve the six-slot commitment described in the saved `script/objective.json`.
- The saved objective has six slots and sixteen variants per slot (16^6 = 16,777,216 candidate tuples). A single classification result is insufficient evidence for this objective.
- Saved responses inspected during this audit show `invalid target slot`, `invalid encrypted embedding`, and `rejected`; none demonstrates acceptance.
- This audit used only local file reads. No service request, process-memory scan, or flag submission was performed.

## Local instance comparison — 2026-09-25

Historical probes compared the container on `127.0.0.1:5001` and the direct binary on `127.0.0.1:5002`. Sampled public/error responses, selected session fields, and one slot PNG matched. This does not establish full server equivalence. A subsequent audit found identical `public_key.b` vectors across four distinct saved local sessions, so the earlier claim of a new public key every session is withdrawn. See `script/server-client-diff.md` for corrected evidence and limitations.

The previous route list omitted the session-creation endpoint. The current `solver/solve.py` is not a protocol client: it does not create a session, retrieve a slot, consume dynamic session values, or send evaluation requests. See `script/server-client-diff.md` for the complete comparison and reproducible probe.

At the time of comparison, host port 5000 was closed; Compose was mapped as host 5001 → container 5000, while the direct process listened on 5002. The two local launch environments also use different fixture flags (`local_test_only` versus `local_debug_only`).

## Consolidated verification review

See `script/local-verification-review.md` for the Vietnamese evidence summary, freshly recomputed cache scores and hashes, local reconstruction limits, and the incomplete `ctf-crypto` workflow audit. These checks establish cache arithmetic only, not challenge completion.
