# Res Impossibilis — offline forensic audit

Status: incomplete. No flag produced or submitted.

## Validated input

Use `script/evidence/mem.clean`: 8,589,332,605 bytes, CRC32 `a27ecaed`, matching the `mem.dmp` member of supplied `dist1.zip`. Other files named mem.dmp/mem.full are incomplete and must not be used.

## Answer evidence

1. Malware account: `tommyxiaomihackerbox@gmail.com`. MEGA file metadata associates `sys_audit_collector` with owner handle `WKgaKPK93KU`; contact records at memory offsets `0x1e9333eb3` and `0x1ea048fa3` map this handle to this email. The logged-in victim account is a different account.
2. Initial malware SHA256: `9ec3d41b5db1baee571dbe1bebff4774b85d61e046edce96a86dd489644ce2e7`. Chromium download protobuf records at `0x20b71e5` and `0x20b740f`, GUID `fde0ecad-4cc1-47d0-b691-faaa00a9095c`, name sys_audit_collector, total/received 23360 bytes. The second record has completed state 1. Parser and original protobufs are under `script/offline_audit/`. This is download metadata evidence; a complete original executable has not yet been recovered independently.
3. Archive password: unresolved.
4. MD5 shown inside captured image: `730f0c0eadc0edb118e4fdc6fbee892e`. Read directly from the restored screenshot (`script/offline_audit/surveillance.png`), with all PNG chunks CRC-verified.

## Evidence and reconstruction

Terminal history records sys_audit_collector reporting 39 files in `/tmp/documents_staging.zip`, then removal of the executable and archive, then execution of kworker_daemon.

MEGA archive file key recovered from browser metadata:
`[2032387434,2144802918,1612300407,-1744597057,376328228,-333502917,137095450,-350496053]`.
The usual MEGA AES-CTR key construction decrypts a buffer at RAM file offset `0x2f3e054` to a password-protected ZIP. Its next virtual page is physically at `0x2f41040`, not adjacent. Eleven local file headers are currently recovered; continuing reconstruction is incomplete. Do not treat `documents_reassembled.zip` as a complete archive.

The first complete encrypted file is `staged/incident_triage_confirmed.txt`, 839 bytes with CRC32 `58e4cad4`. Searching 39,706,386 complete printable memory strings as passwords did not find a verified password.

The surveillance component includes PyArmor-obfuscated Python 3.9 metadata. Its image envelope is documented in memory as `IMGV` + big-endian uint32 payload length + 16-byte IV + AES-128-CBC ciphertext with PKCS7 padding. Key identifier: `3e91fa12`. Functions include CryptoVaultManager.seal_buffer_into_vault and DisplayCaptureEngine.capture_active_screen. The docstring mentions a generated console, but the actual restored PNG is a GNOME screenshot. The required MD5 is visible in the file manager search box. VAULT_MASTER_KEY is `3e91fa1288cd04b2715a90ef234761d8`, recovered as a 16-integer tuple in marshalled ImplantConfig at offset `0x6eae7c8` (near IMGV). Alternating known plaintext/ciphertext prefix matches reconstructs the fragmented image without executing the agent. `stitch_vault.py` reproduces the image and validates each chunk CRC.

## Limitations / failed checks

- Adjacent physical carving of 23360-byte ELF candidates gives invalid section tables and an incorrect SHA256; these are not valid copies of the original malware.
- The supplied memory requires Linux symbols for CentOS Stream 9 kernel 5.14.0-22.el9.x86_64; Volatility pslist could not initialize without suitable symbols.
- After enabling TShark TLS record reassembly, 121 distinct ClientHello randoms were found (87 TCP, 34 non-TCP/QUIC), 57 more than the previous extraction. The RAM TLS key logs still match none of them. Suricata independently reports 87 TLS sessions. See `script/offline_audit/soc/README.md`.
- Several intact PNGs were carved; the large image inspected was MEGA UI artwork, not the requested console screenshot.

All new scratch artifacts and parsers are isolated under `script/offline_audit/`. Recovered binaries have not been executed. No live service or captured account has been accessed.

## ZIPCrypto and SOC follow-up

bkcrack recovered ZIPCrypto initial keys `670e8462 306591b4 8372919d`. The independent `verify_zip_evidence.py` script decrypts 10 complete entries from the partial archive and checks every plaintext size and CRC32. The eleventh entry is incomplete. This recovers content, not the original archive password.

The first ZIP encryption header is `d534070c1972f229fcfec458`; its first eleven bytes match glibc rand output beginning at index zero with seed 1788885121. `zip_evidence.json` records the bounded seed/position check. This alone does not establish password generation or rule out reseeding.

Suricata 8.0.6 processed all 740,595 packets offline with zero TCP reassembly gaps and zero TLS parser errors reported. No signature rules were loaded. All 488 HTTP requests belong to the other host's Ubuntu activity. The victim PCAP was isolated to 27,080 packets / 27,345,340 bytes. Existing Zeek flow data and Suricata TLS events agree on the collector download and suspected MEGA upload endpoints; their TLS payloads remain encrypted.

## MEGA research relevance and central-directory recovery

The user suggested the historic MEGA attack. Verified primary sources:
- https://cryptohack.org/challenges/web/ — Cloud section, Megalomaniac 1–3, explicitly models server interaction with logging-in clients.
- https://mega-awry.io/ — MEGA: Malleable Encryption Goes Awry (2022), active malicious-server key recovery. The page also links Cryptanalyzing MEGA in Six Queries.

Applicability assessment: these attacks target MEGA sharing/node keys and require active client interactions; an ordinary passive capture does not supply that oracle. We already recovered the archive node key from memory. An independently password-encrypted ZIP remains encrypted after removing the MEGA layer, so this research does not directly recover answer 3. No remote attack or account access was performed.

Recovered encrypted ZIP EOCD at memory offset 0x1cd8fbe, archive logical offset 65386. Exact plaintext: 504b050600000000270027007f0b0000ebf300000000. This confirms total size 65408, 39 directory records, central-directory offset 62443 and length 2943. Saved archive_central_directory.bin and archive_central_records.json under offline_audit. This establishes metadata completeness, not complete recovery of all file contents. The new recover_archive_central.py tracks known bytes and exports only complete, CRC-verified plaintext entries.

Correction of a discarded lead: the 60-byte Base64 suffix considered as a possible audit-log artifact belongs to a longer Coccoc new-tab URL parameter. It is not evidence of the ZIP password. Kernel inode analysis reports the actual 60-byte audit log has no resident page-cache pages; its content has not been recovered.

Central-guided reconstruction verified: `python script/offline_audit/recover_archive_central.py` recovered 16256/65408 bytes with an explicit known-byte mask, and decrypted 14 complete entries, all matching CRC32 and plaintext length (previously 10). The four newly complete entries are addons.json, state.json, session-state.json and xulstore.json. Most middle archive pages remain absent from this header-based search; metadata for all 39 entries is intact. Password remains unknown.

## Parallel investigation — 37/39 archive members verified

The user explicitly authorized collaboration, then prioritized completing the39 archivefiles. Three agents investigated archive recovery, password mathematics/content verification, and kernel pagecache. Independent state/verifier checks passed; additional boundedpasswordsearches returned no candidate.

Current canonical plaintext collection: `script/offline_audit/recovered39/`, manifest plusREADME. Reproducer `root_files/assemble_verified_files.py` verifies eachmember's expectedsize/CRC and everyavailablecorrespondingciphertext byte byreencryption. Count37. Ofthese31werefullydecryptedfromRAM, entry27usesverifiedFirefoxreference+RAMrecovery, entry31completes99missingbytesfromknownprefix, and32–35are boundedofficialFirefoxdefaultreconstructions with exactCRC/size matches.

Entry27extensions.json recovery: acquired onlystaticreference browser/omni.ja fromofficialMozillaFirefox91.3.0esr package; no code executed. ExactcapturedRPMversion91.3.0-1.el9 agrees. Wikipedia localeordering followsnsZipArchive rolling37hashmod256overdirectorynames, withcentraldirectoryorder tiehandling anddefaultEnglishfirst. Known21701-byteprefix and allfieldpositionsmatch. DerivedcipheranchorslocateMEGApagesatRAM0x1592040 and0x2abe040; actualBingUUID48036d49-679c-4ead-bb61-fc0aee57529f recoveredfromRAM. Full37583-bytefileCRC20a2f078 valid;32223observedciphertextbytesmatch. SHA2560fdc36387d24f69187849a35cd27bb487a80f2f38f4604684beb3921b2da6698. Seeagent_archive/README.md andextensions_final_report.json.

Entry37AlternateServices tail: exactfilecachetail1302bytes was independentlylocatedviaFirefoxinode. bkcrack on621overlappingobservedcipherbytes yieldswindowkeys5ffbd4a3 53a546c3 1f074394 atZIPlogical61420. Reversing681knownplaintextbytes providesearliercipheranchors, locatingMEGAmemorypage0x1d6f040=>ZIPlogical57324. ReverseZIPCrypto decryptionrecovers4717plaintextbytesstartingoriginaloffset681, matchingall1302originaltailbytes. Seeroot_files/recover_alternate_tail.py, alt_partial_report.json and37_AlternateServices.partial.txt. Inlinebackwardpage-decryption step stillneedsconsolidationintoreproducer.

Currentnearcompletearchive+mask inagent_archive has63684/65408known/derivedbytes. Unknownonly[55530,56573)HSTS1043bytes and[56643,57324)AlternateServices681bytes. ActualRAM vsderivedprovenancepreserved; do notclaimall39filesorcompletearchive.

KernelmanualwalkfoundCR3physical1294000. mem.dmp cache itself appearsinacquisition, withstalepagecontents/mappingsatdifferenttimes. This explainsrepeateddataandinvalidcollectorpageattribution; no deliberatezeroingclaim. ActualFirefoxprofileinodes haveevicted/shadowentries forHSTS/handlers andpartialextensions/Alternatecache. Seagent_collector/README.md andhelpers.

Searchcorrectness: rg--replacewithshortertextshiftssubsequentmatchoffsetsonsameline. Rootscanners nowuseJSONabsolute_offset+submatches.start. Allaffectedfinalrootresultsrerununchanged; regressionfixturezzzABCDEFxxxABCDEF confirmscorrectoffsets3,12.

Contentreview37files: malformedKDBX oversizedfirstfield, mockXLSXpayload, TLSkeylogsyntaxvalidbutclientrandomabsentfromall121capturedClientHellos; fakecredentialsandAIinstructionsignoredasdata. 2639distinctcontentderivedsequenceswithsubstrings<=128yieldnoZIPpassword. extensionsmetadatahas16bundled-lookingaddons, noconfirmedattackerextension. Seeagent_password/recovered_files/CONTENT_REVIEW.md.

PassiveTLS87fallback: completeclient68050/server6288bytes, noTCPgaps/conflicts, TLS1.3suite1301. 88AES128schedule/layoutcandidates ×16records yieldzeroGCMnonce-structurematches. OriginalZIPpasswordstillunknown, overall3/4answers; noflag/submission.

## Password formation follow-up

The user redirected work to the original password and how it was formed. The latest consolidated evidence is `script/offline_audit/root_state/PASSWORD_FORMATION_STATUS.md`.

An independent glibc model verifies 363 bytes in 33 directly observed ZIP headers. They start at RNG output zero for effective seed 1788885121, then advance 11 draws per member. This strongly contradicts a simple password-generator phase consuming the same uninterrupted RNG state before header generation. It does not exclude password generation followed by reseeding. Imports such as gethostname/fgets/strpbrk/snprintf are confirmed, but no call site or format string proves a hostname/machine-id formula. The 60-byte audit log does not establish password length.

TLS75 raw-key recovery is now complete for all 8,589,332,417 segment-contained 16-byte RAM windows, with no nonce-filter match. Existing schedule-derived layouts also fail. Arithmetic and TCP reassembly were independently checked. This covers literal AES128 keys for the selected record, not all possible TLS secret representations.

New code-recovery checks found no collector mapping via swapped leaf PTEs or stale VMAs. Captured zswap.enabled is zero; six /proc/swaps buffers report zero usage. A scan of ZIPCrypto/CRC/compact-hash constants found no attributable collector code. A conventional 14-entry unwind-header search found 33 candidates but none with the collector's code-address range. Exact scopes and limitations are preserved in the consolidated report and linked agent artifacts.

No original password, password-generation formula, or complete original executable was recovered in this follow-up. Archive recovery remains 37/39 verified members. The AlternateServices backward decryption has now been consolidated in `root_files/recover_alternate_tail.py`, superseding the earlier note that this step was pending.

## Additional password negative evidence (2026-09-30)

`check_wordlist.c` is a small local verifier for the recovered initial
ZIPCrypto state `670e8462 306591b4 8372919d`. It checked all 14,344,392 lines
of `/usr/share/wordlists/rockyou.txt` with zero matches. Piping Hashcat's
`best66.rule` expansion of that same list through the verifier checked
946,729,410 candidates, also with zero matches. A Z3 model of a 12-character
printable preimage reached `unknown` after its 60-second bound; it does not
establish a candidate. These probes do not recover the original password.
