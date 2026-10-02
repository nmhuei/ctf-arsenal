# Password formation: evidence and remaining gap

Original password and its construction remain unknown. No flag was produced.

## Established behavior

- The post-password ZIPCrypto state is `670e8462 306591b4 8372919d`. It is an exact candidate verifier, not the plaintext password.
- An independent glibc model matches **363 bytes in 33 RAM-observed encryption headers**, member indices 0 through 31 and 38. The effective seed is `1788885121`; header i begins at output 11*i. Reconstructed headers 32 through 37 were excluded from the evidence count.
- Each header has 11 low bytes from rand followed by one CRC high byte. The archive metadata uses stored data, no extra fields or comments, and the fixed historical timestamp 2022-09-01 13:00.
- Collector ELF imports include gethostname, fgets, strpbrk, snprintf, srand and rand. No recovered call site links these functions to password construction.

## What this says about formation

| Model | Evidence status |
| --- | --- |
| Seed RNG, consume draws to form password, then continue the same state into ZIP headers | Strongly contradicted by header 0 beginning at draw 0 under the ordinary continuous-state model |
| Form password earlier, then reseed before writing headers | Compatible, unproved |
| Derive password from hostname or file contents | Compatible, unproved; imports alone do not identify the file or formula |
| Use a fixed, externally supplied, or separately generated password | Compatible, unproved |
| Reset the same RNG seed separately for every member | Contradicted by differing header prefixes |

The actual hostname and machine-id are known, but no evidence yet establishes that either enters the password. The audit log's 60-byte length does not establish password length without its format.

## New recovery checks completed

1. **TLS75:** every segment-contained 16-byte window in mem.clean was tested as a raw AES128 key against the final server record, with independent arithmetic and TCP-reassembly checks. No match. This does not cover traffic secrets requiring derivation, differently represented keys, or keys absent at capture time. See ../agent_password/tls87/RAW_KEY_REVIEW.md.
2. **Swap and old mappings:** 1,170 address walks yielded no nonpresent leaf identifying a swap slot; 679 segment-boundary patterns yielded no validated collector VMA. The captured zswap.enabled parameter is zero, and six /proc/swaps buffers report zero usage. See ../agent_collector/password_followup/code_route_audit.md.
3. **Instruction constants:** the agent reviewed 5,375 ZIPCrypto/CRC/compact-hash constant hits. No code was attributable to the collector; permissive arithmetic coincidences were retained as unverified. See ../agent_password/code_constants/README.md.
4. **Unwind header:** GNU_EH_FRAME metadata motivated a conventional 14-entry header search with four pointer distances. All 33 matching headers failed the collector code-address range check. This bounded encoding model does not exclude every possible unwind representation. See find_collector_eh_frame.py and eh_frame_candidates.json.
5. **Audit log:** its filesystem extent and extent-free metadata were found, but no content buffer. See ../agent_collector/password_followup/README.md.

## Reproducible header audit

Run from the challenge root:

```sh
python -B script/offline_audit/agent_archive/zip_writer_fingerprint.py
```

Full reasoning about observational constraints and library differences is in
../agent_archive/ZIP_PASSWORD_FORMATION_AUDIT.md.

## Decisive evidence still missing

An original collector code/data fragment containing the input paths and password formatting/derivation, or the audit log contents, would discriminate between the remaining models. Further dictionary expansion without one of these anchors would not establish how the password was formed. Every eventual candidate must match all three ZIPCrypto state words and be checked against archive contents; a constructed equivalent preimage would not prove the original answer.
