# Timeline

- 2026-07-26T04:31:40+07:00 [lead] Initialized scope for D3CTF ghost web target.
- 2026-07-26T04:32:15+07:00 [cie] Mapped frontend assets: `/assets/index-cTcmaRYN.js` loads `/assets/crypto.worker-DW2VSort.js`.
- 2026-07-26T04:33:00+07:00 [cpe] Reproduced encrypted gateway client and confirmed `search` operation over `/api/session/guest`, `/api/transport/bootstrap`, `/api/gateway`.
- 2026-07-26T04:34:00+07:00 [cpe] Confirmed SQLite SQL injection through search query; dumped schema for `knowledge_base`, `logs??`, `User`, and `q_8f3c1a72d90e4b65`.
- 2026-07-26T04:39:00+07:00 [cpe] Dumped SQLite raw pages via `sqlite_dbpage`; recovered deleted `Ghost_Zero` row pointing to `/test/7f9c18a2e44d/fe291443882d55af94bff1f9cddffb73.pcap`.
- 2026-07-26T04:40:00+07:00 [cpe] Downloaded deleted PCAP; it contains legacy `/ddddddtestStat` bootstrap and `/api/auth/exchange` issuing an admin JWT, but signatures are sanitized/invalid on live replay.
- 2026-07-26T04:44:00+07:00 [cre] Recovered current primary RS256 public key from guest JWT signatures; HS256, embedded JWK, JKU/X5U/X5C, and simple RSA weak-key paths did not bypass live verification.
- 2026-07-26T04:59:00+07:00 [cpe] Checked route normalization, Host/X-Forwarded variants, debug headers, direct internal ports, basic HTTP desync, token-source ambiguity, and guest token parameter influence; no admin token recovered.
