# Crypto workflow: offline verification result

Overall challenge status: **UNSOLVED**. The supported result is cache integrity and integer classifier arithmetic, not an end-to-end solution.

## References reviewed

The `ctf-crypto` skill, `references/attack-router.md`, `references/orchestration.md` (including all six lattice stages), and `references/mathematical-handoff.md` have now been read. Reading them now does not establish that earlier lattice experiments followed their requirements.

## Classification and evidence

The supplied cache and metadata expose an integer affine classifier. The saved objective describes a separate six-slot hash commitment. These are distinct layers. Neither the existence of a historical lattice script nor an apparent candidate proves the complete cryptographic construction or a weakness in it.

The inexpensive checks performed here are file hashes, magic, dimensions, record lengths, signed-byte decoding, and all cached classifier evaluations. No cryptographic weakness is established by these checks.

## Explicit mathematical model

For each record v, the observed embedding is e_v in Z^12, decoded from signed int8 bytes (range -128..127). Published metadata gives W in Z^(4×12) and b in Z^4. Compute l_v = W e_v + b over the integers, without modular reduction or int8 multiplication overflow. Coordinates retain file order; W rows correspond to output classes.

The margin is the greatest logit minus the second greatest. For deterministic reporting, ties are ordered by increasing class index; this convention is not claimed to reproduce the server's tie behavior. The current data has no top-class ties. The opaque 32-byte fields are excluded from this model because their semantics were not established by these checks.

The model computes a published layer from observed inputs. It does not recover a secret variable, establish image-to-embedding equivalence, or model all session acceptance constraints.

## Reproduce

Run from the challenge workspace:

```sh
python3 script/offline_cache_verify.py > script/offline-cache-verification.json
```

The verifier uses only Python's standard library and reads three supplied local data files. It does not import or execute the historical solver. It checks every cached record and reports all 16 embeddings, logits and margins. A hash/layout violation raises an error instead of reporting success.

Reference result: 744-byte cache, one entry, 16 records. Record 6 yields logits [76, -75, 156, 168] and margin 12. Full expected logits and source hashes are in `local-verification-review.md`.

## Remaining requirements and expert decision

- The full original acceptance constraints have not been independently verified.
- No minimal proof of a cryptographic weakness is established here.
- The vision pipeline has not been regenerated and compared with reference embeddings.
- No server was started or reconstructed during this step. The supplied Dockerfile packages an existing binary; source equivalence is unproven.
- No expert handoff was created. This classifier calculation has no hard mathematical blocker, and the skill explicitly excludes routine parsing/implementation from expert escalation.
- No agy or Astra invocation was made. Exploitation and secret extraction were not delegated.

`worker-report.json` remains `not_verified` / `unsolved`. Offline arithmetic checks cannot promote that status to `passed`.

## Local server/client diagnosis

Historical results from `script/compare_local_instances.py` matched sampled public/error responses between the container (5001) and direct binary (5002). This does not establish full server equivalence or successful acceptance. Static review independently shows that `solver/solve.py` never performs the protocol and substitutes a Compose/process flag for verifier acceptance. The report also incorrectly characterized `public_key.b` as changing every session: four saved local sessions have identical vectors. See `script/server-client-diff.md` for the corrected scope and fresh offline verification.

The host port check also found no listener on 5000. The running mappings are Compose `5001 -> 5000` and direct process `5002`; a client pointed at local port 5000 fails with connection refused before protocol handling.

Fresh smoke verification in the current turn passed the loopback route assertions and cache verifier. No mathematical failure was produced, so no Astra handoff was created.
