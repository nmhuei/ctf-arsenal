# Passive TLS75 RAM key review

Purpose: recover the captured collector download for static analysis of the original ZIP-password generation. No executable is run and no network endpoint is contacted.

## Exact target and method

Target is TLS75 server record 6, offset 29657, TLS1.3 AES128-GCM-SHA256. AAD is `1703030013`; ciphertext is `e7c89d`; tag is `56c5067b62519f9f744c1e2abaa 32d07`. The three-byte inner plaintext may be an alert (inner type 21).

For each candidate 16-byte key actually present in RAM, compute H=AES_K(0), GHASH of the three padded AAD/ciphertext/length blocks, then J0=AES^-1_K(tag XOR GHASH). A 96-bit GCM nonce requires J0 to end in `00000001`. This is only a 32-bit candidate filter: any hit must authenticate separate captured records using a consistent TLS record sequence/base IV. The validator tests server bulk records 4/5, including the expected record 6 sequence 3 and bounded alternatives 0..15.

The image is parsed as LiME segments. Physical 16-byte alignment corresponds to file offsets modulo 16 of 0, 0, 15, 14 in its four segments. Candidate windows never cross segment boundaries. All-zero keys are checked once; further zero instances are skipped. No entropy, printable-character, or repeated-word exclusion applies.

## Independent controls

The native implementation passes its synthetic GCM nonce fixture and wrong-key control. Archive agent independently validated the AES implementation with 1000 random encrypt/decrypt cases and the nonce inversion with 1000 random GCM records. The shared CLMUL GHASH helper passed 4099 independent reference vectors. See `agent_archive/tls87/native_aes_audit.json`, `ghash3_validation.json`, and `tls75_checked/integrity_summary.json` for controls and independent PCAP reassembly verification.

## Completed aligned scan

`native_full.log`: 536,833,277 physical-aligned positions, 420,510,154 nonzero candidate instances tested, 116,323,123 repeated all-zero instances skipped after testing zero once. Zero filter hits; runtime 6.911648 seconds on four threads. This result alone does not cover packed/unaligned keys, alternate memory byte layouts, or keys absent from the capture.

## Reproduction

Compile `raw_aes_scan.c` with `-O3 -maes -mpclmul -mssse3 -fopenmp`. Run against `script/evidence/mem.clean` with `--benchmark`, `--full` (physical 16-byte alignment), or `--all-bytes` (all byte positions). Capture stdout candidate JSONL and stderr metrics separately. Run `validate_native_hits.py` against a completed candidate JSONL to corroborate independent records.

## Completed all-byte scan

`native_allbytes.log`: all 8,589,332,417 segment-contained 16-byte windows visited, 6,777,982,065 nonzero candidate instances tested, 1,811,350,352 all-zero instances skipped after zero was tested once. Zero nonce-filter hits. Runtime 145.339689 seconds on four threads. This excludes a verbatim copy of the selected final server-record AES128 key within captured physical segments, under the verified target and arithmetic assumptions. It does not exclude alternate memory representations, HKDF input traffic secrets, or keys absent at capture time.

## TLS75 schedule-derived candidates

`test_tls75_gcm_schedule_keys.py` / `tls75_gcm_schedule_results.json`: 22 unique AES128 schedule keys, with original, reversed whole key, reversed bytes within each 32-bit word, and reversed word order, give 88 candidates. Tested against all seven captured encrypted TLS75 records (616 key/record pairs): zero nonce-filter hits. Suite 0x1301 is parsed directly from the captured ServerHello. AES256 schedule rows are excluded because the negotiated suite requires a 16-byte key.

## Why zero random filter hits is plausible

6,777,982,065 is a count of candidate *instances*, not distinct keys. Even if every instance were a distinct independent random key, the expected number of accidental 32-bit suffix matches would be only 1.578; an idealized Poisson model gives a 20.6% probability of zero matches. Repeated keys have identical outcomes and lower the effective number of trials. Thus zero matches is not, by itself, evidence of a broken scanner.

A bounded descriptive sample of 65,536 equally spaced windows found 13,828 zero windows; the remaining 51,708 nonzero instances contained 47,097 unique keys and 4,611 duplicate instances. The most repeated nonzero key appeared 1,226 times. This demonstrates duplicates but does not estimate the exact full-image unique count. See `zero_hit_audit.json` and `audit_duplicate_sample.py`. No further TLS scanning was performed for this audit.

Confidence in the negative comes from positive synthetic fixtures, randomized independent AES/GHASH/nonce controls, exact independently reassembled target bytes, and correct segment/window coverage. The original ZIP password remains unresolved; this review does not establish any password-generation hypothesis.
