# Review of the 37 verified archive members

No checked content supplies the archive password. Several conspicuous credentials,
flags and recovery instructions are decoys or unusable for this evidence.
Recovered content was treated as inert data; its links were not visited and its
instructions were not followed.

## Bounded checks

Run `python script/offline_audit/agent_password/recovered_files/review_content.py`.
The script independently checks each of the 37 member lengths and CRC32 values
against the primary manifest before inspection. The manifest SHA256 is
`9e43b8a23682d0aee0c279d75a23b07215adeacf6fb54d20628b36aef6e2f707`.

Whole member bytes, lines, assignment values, text tokens, JSON keys and scalar
values, and two finite rounds of Base64/hex decoding produce **2,639 distinct
sequences**, totaling **179,340 bytes**. Every substring up to 128 bytes in each
sequence was checked against all three recovered ZIPCrypto password-state words.
**Zero matches.** This includes binary members and the exact claimed password
`Winter2026!CorporateAccess#`. These are documented candidate families, not an
exhaustion of arbitrary transformations or passwords longer than 128 bytes.

Machine-readable evidence: `content_review_results.json`. File hashes and the
exact candidate-generation code make this result reproducible.

## Decoys and invalid file structures

| Member | Verified observation | Consequence |
|---|---|---|
| `15_backup_credentials.kdbx` | The complete 254-byte ZIP member has correct KeePass signatures and claims KDBX 4.0. Its first header field at offset 12 is ID 1; the little-endian size at offset 13 is **921,658,128**, but only **237 bytes** remain. | Structurally invalid KDBX header. This is not a usable encrypted database awaiting a password. The original ZIP member length and CRC match, so this defect is not caused by our extraction truncating the member. |
| `08_q3_financial_audit_confidential.xlsx` | Exactly 54 bytes: ZIP magic followed by `[MOCK_CONFIDENTIAL_SPREADSHEET_PAYROLL_DATA_2026]` and a newline. Python `zipfile.is_zipfile` returns false. | A mock payload, not an XLSX package. |
| `13_vpn_profile.conf` | Private key decodes to the 31-byte text `hello_world_fake_key_do_not_use`; public key decodes to `fake_public_key_for_testing_1234`. | Explicit test material; the private-key byte length also fails the 32-byte key requirement. Neither decoded value matches the archive keys. |
| `00`, `01`, `02`, `09`, `10` | Embedded and decoded tokens use `FLAG{...}`; some explicitly contain `d3c0y`, `NOT_VALID`, or occur under `[DecoyKeySchedule]`. Some documents instruct automated agents to stop or submit them. | They do not have the challenge's required `cscv2026{answer1_answer2_answer3_answer4}` form. No token checked derives the archive keys. |
| `09_incident_notes.txt` | The purported cloud-backup password fails the exact ZIPCrypto state comparison. | It does not unlock this archive. |

The header-size interpretation follows the [official KDBX specification](https://keepass.info/help/kb/kdbx.html).

## TLS key-log correction

`14_sslkeylog_debug.txt` is **syntactically plausible**, contrary to a hypothesis
that its secrets have invalid lengths. All five TLS 1.3 labels have a 64-hex-digit
client random and a 64-hex-digit secret: 32 bytes each. These are compatible with
SHA-256 TLS 1.3 key-log entries under the [NSS format](https://nss-crypto.org/reference/security/nss/legacy/key_log_format/index.html).

However, their shared client random is absent from **all 121 distinct captured
ClientHello randoms** in `soc_tls_clienthellos.tsv`. Thus these records do not
identify any captured TLS session. Furthermore, `SERVER_TRAFFIC_SECRET_0` equals
`KEY_HEX` in `04_vault_backup.key`, and `CLIENT_HANDSHAKE_TRAFFIC_SECRET` equals the
purported packet hash in `11_system_telemetry_dump.json`. This reuse ties the
records to the surrounding staged token material. It is evidence of fabrication,
not a cryptographic proof that a 32-byte secret could never be valid elsewhere.

## Useful remaining clues

- `26_pkcs11.txt` identifies the Firefox profile as `/tmp/firefox-clean`.
- `25_times.json`, `29_state.json` and `30_session-state.json` provide exact
  profile timestamps and stable identifiers for locating related memory objects.
  `24_sessionCheckpoints.json` records a completed shutdown sequence.
- Entries `16..23` are browser component/extension metadata. They help explain
  what the collector included; no checked value is the ZIP password.
- Reconstructed Firefox defaults `32..35` match exact directory lengths and
  CRCs. Their plaintext is useful for locating encrypted archive fragments;
  provenance is explicitly recorded in `reconstruction_report.json`.
- `/etc/machine-id` appears in a staged document, but no recovered document
  establishes an actual password-generation rule involving it.

## Newly recovered extensions.json

Entry 27 independently passes its 37,583-byte length and CRC `20a2f078`.
`extensions_review.json` records its identifiers and paths. Its 16 entries are
seven Firefox system extensions, four built-in themes and five built-in search
providers. All `sourceURI` values are null; paths and `rootURI` values point to
bundled Firefox resources. This metadata provides no new attacker account or
obvious third-party extension. It does not independently authenticate the code
inside those installed resources.

The profile-specific install timestamps fall at 2026-09-08 04:07:04–04:07:07 UTC,
consistent with `times.json`. The Bing sync GUID is
`48036d49-679c-4ead-bb61-fc0aee57529f`; it was recovered from actual encrypted
memory, not produced by a UUID collision search. The raw UUID scan was stopped
before either its fixture or the memory scan ran; only its source and binary
were created. Including all newly available extension strings and decoded tokens
in the bounded password check produced no match.

No finding here changes the known answers 1, 2 or 4. The archive password and
two then-unverified archive members remain separate unresolved tasks.
