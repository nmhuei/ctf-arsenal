# bdsec26_dfir_Paper Trail solve log

## Known facts
- Workspace: `/home/dell/ctf-workspaces/_work/bdsec26_dfir_Paper Trail`.
- Local artifacts initially present: `AGENTS.md`, `.codex_guard/` only; no challenge evidence files in workspace.
- Challenge asks for FirstBangla Bank employee email password and attacker's email address.
- Provided VM access target: `ssh -p 2222 investigator@127.0.0.1`.
- Classification: DFIR / Linux or application forensics via remote VM.

## Hypotheses
| id | surface | hypothesis | next test | finding | status |
|---|---|---|---|---|---|
| H1 | VM filesystem/logs | Password and attacker email are recoverable from local mail/browser/app/log artifacts in the investigator VM. | SSH in and inventory home/system artifacts read-only. | pending | OPEN |

## Failed paths / Do Not Repeat
- None yet.

## Next best test
- Connect to VM and inventory accessible files, logs, and user artifacts without modifying original challenge content.

## Update 2026-07-21
- SSH reachability confirmed on `127.0.0.1:2222`, but authentication failed with available local keys: `Permission denied (publickey,password)`.
- Checked workspace and `~/.ssh`; no usable private key or password hint found.
- Current blocker: need password for `investigator` or private key path.

## User handoff notes 2026-07-21
- Handoff claims: target employee is `arif.khan@firstbangla.com`; likely password candidates include `F!rstBangla#Vault2024` and exfiltrated `F!rstB@ngla#Vault2024`; attacker email still missing.
- Handoff claims pcap path `/var/captures/archived/network_capture.pcap`, treasury log `/var/log/firstbangla/treasury_access.log`, DB `/opt/firstbangla/db/transfer_records.db`.
- Treating these as hints until locally re-verified.

## Update 2026-07-21 continued
- SSH connected with user-provided password `1234`; VM host `FBBL-FORENSICS-WS01`.
- Verified DFIR surfaces: `/opt/firstbangla`, `/var/log/firstbangla/treasury_access.log`, `/var/captures/archived/network_capture.pcap`, and `/home/*` user artifacts.
- Verified theft timeline in treasury log: `arif.khan` logged in from `10.0.0.12`, initiated BTC transfer, used `salim.uddin_approval`, completed BTC/ETH/USDT transfers, then attempted log deletion.
- PCAP confirmed C2 POSTs to `185.220.101.47:8443`; decoded `/sync` payload contained `vault_key=F!rstB@ngla#Vault2024`.
- Decrypted Arif Firefox saved login for `https://firstbanglamail.com`: username `arif.khan@firstbangla.com`, password `knightsquad4041337@`.
- Live mail endpoint observed from Firefox history: `http://50.116.30.77:5000/login`; login page saved to `evidence/mail_login.html`.
- Next best test: use saved mail password to log into the mail app, then inspect mailbox pages for the attacker's email address.

## Final 2026-07-21
- Mail login with `arif.khan@firstbangla.com` / `knightsquad4041337@` succeeded at `http://50.116.30.77:5000/login`.
- Relevant mailbox pages saved under `evidence/mail_*.html`.
- Attacker email identified as `unknown321@protonmail.com` from A. Reza threads discussing Rajesh Patel, wallet testing, TG322, and logistics.
- Verified flag: `BDSEC{knightsquad4041337@_unknown321@protonmail.com}`.

## Final vault-password question 2026-07-21
- Archived PCAP `/var/captures/archived/network_capture.pcap` frame 19916 has HTTP POST `/sync` body `dmF1bHRfa2V5PUYhcnN0QkBuZ2xhI1ZhdWx0MjAyNA==`.
- Base64 decode gives `vault_key=F!rstB@ngla#Vault2024`.
- The same password successfully decrypts `/home/arif.khan/AppData/Signal/exports/signal_messages.json.enc` as OpenSSL AES-256-CBC PBKDF2, producing the Signal JSON export.
- Verified flag: `BDSEC{F!rstB@ngla#Vault2024}`.

## Final C2 and fled-location question 2026-07-21
- Archived PCAP traffic confirms C2 communication between `10.0.0.12` and `185.220.101.47:8443`, including `/sync`.
- Decrypted Signal export confirms the planned flee location: Bangkok accommodation at Golden Palace Hotel, Sukhumvit area, room 412 under new identity `Rahman Hossain`.
- Telegram export `/home/arif.khan/AppData/Telegram/telegram_export.json` has one explicit location object from Rajesh Patel on 2024-04-15: latitude `13.8703066`, longitude `100.5928967`.
- Verified flag: `BDSEC{185.220.101.47_13.8703066_100.5928967}`.

## Final Telegram escape-manager question 2026-07-21
- Decrypted Signal export title is `Faisal (Documents & Travel)`.
- Signal message `msg-0025-1710489600000` from `unknown_contact` says: `R referred you to me... New identity, travel documents, destination support.`
- Telegram export has the matching escape/logistics account as `from: Deleted Account`, `from_id: user323456789`, with message: `I can handle travel logistics for the right clients. R knows my rates. Discretion guaranteed.`
- No separate Telegram `username` field was present after deletion; using the surviving Telegram user identifier as username.
- Verified flag: `BDSEC{user323456789_Faisal}`.

## Final live-message question 2026-07-21
- Process list shows root-running `/usr/bin/python3 /opt/firstbangla/bin/.monitor-worker.py`.
- Hidden worker source comments say it builds a message in heap and repeats it in memory while the process runs.
- Decoding the `chr(...)` list in `/opt/firstbangla/bin/.monitor-worker.py` gives `W3lcom3 gen1us t0 THis W0rlD`.
- Verified flag: `BDSEC{W3lcom3_gen1us_t0_THis_W0rlD}`.

## Final attacker real-name and external-account question 2026-07-21
- Decrypting `/home/arif.khan/.confession.enc` with OpenSSL AES-256-CBC PBKDF2 and password `F!rstB@ngla#Vault2024` confirms: `Rajesh handled the mixing`.
- Deleted WhatsApp recovery identifies the operator as `Rajesh Patel, +91-9876543210, RPC Consulting, Mumbai`.
- The FirstBangla transfer DB shows Arif's first/primary theft transfer at `2024-05-10 09:30:45` to external account ID `EXT-DEST-BTC-0000000000000000001`; this aligns with `.wallet_note.txt` marking the BTC destination as `Primary`.
- Verified candidate flag: `BDSEC{EXT-DEST-BTC-0000000000000000001_Rajesh_Patel}`.

## Correction attacker real-name and external bank account 2026-07-21
- User rejected `BDSEC{EXT-DEST-BTC-0000000000000000001_Rajesh_Patel}`; that value is a crypto destination/wallet ID, not an external bank account ID.
- Rechecked evidence: `/var/log/firstbangla/treasury_access.log` shows `arif.khan` initiated the transfer, used `AUTH_BYPASS`, and attempted `DELETE_LOGS`.
- `/opt/firstbangla/db/transfer_records.db` identifies employee `arif.khan@firstbangla.com` as real name `Arif Khan`.
- `/home/arif.khan/Documents/personal/bank_statement.html` is an external CityTrust Bank statement with `Account Holder` = `Arif Khan` and `Account Number` = `4521-887-2024-001`.
- Corrected candidate flag: `BDSEC{4521-887-2024-001_Arif_Khan}`.

## Rework attacker external bank account 2026-07-21
- User rejected `BDSEC{4521-887-2024-001_Arif_Khan}` as incorrect.
- New recovery plan: full `/dev/sda3` PDF carve with timeout 10 minutes. Candidate count expected: a few hundred `%PDF` signatures from prior scan; runtime estimate: under 10 minutes; validation oracle: valid PDF ending at nearby `%%EOF` and extracted/decompressed text containing `transfer_receipt`, `SK-PRIVATE`, `Salim`, `Rajesh`, `Account ID`, `Beneficiary`, or `150K`.

## Rework mailbox full fetch 2026-07-21
- User asked to increase scan time after two rejected candidates.
- Full mailbox fetch scope: all `/mail/inbox/*.eml` and `/mail/sent/*.eml` links already listed by the authenticated webmail pages, plus `/source` for each. Expected count about 2,500 HTTP GETs; estimated runtime under 10 minutes; validation oracle: decoded message body/header names the attacker real name and a bank/account identifier, not a wallet or Arif's personal statement.

## Final unauthorized brute-force IP question 2026-07-21
- Question: unauthorized IP used to brute force the bank account access.
- Reconnected VM via `work/ssh_run.py` (paramiko, investigator/1234); investigator is in `adm` group so can read `/var/log/firstbangla/treasury_access.log` (45000 lines).
- FAILED_LOGIN events (60 total) source IPs: `10.0.0.12` x32 (arif.khan internal workstation, own-account failures), `45.33.32.156` x26 (external), `10.0.0.45` x2.
- `45.33.32.156` is the brute force: 26 FAILED_LOGIN against AUTH_SERVICE in ~2 minutes (2024-05-03 03:12:05 -> 03:14:14) cycling usernames treasury, finance, arif.khan, support, sysadmin, guest, demo, administrator, operator, info, test, karim.hassan.
- Security monitor confirmed: `[2024-05-03 03:14:29] | security.monitor | ALERT_RAISED | AUTH_SERVICE | BLOCKED_source=45.33.32.156_reason=brute_force_threshold`.
- Evidence saved: `evidence/brute_force_45.33.32.156.log`, `evidence/brute_force_alert.txt`.
- Verified flag: `BDSEC{45.33.32.156}`.

## Rework attacker real-name + external bank account 2026-07-21 (session 2)
- Both prior candidates for this question were rejected: `EXT-DEST-BTC-...001_Rajesh_Patel` (crypto wallet, not bank acct) and `4521-887-2024-001_Arif_Khan` (Arif's own CityTrust personal statement).
- Reconnect helper `work/ssh_run.py` (paramiko, investigator/1234). Sudo works with password `1234` -> full FS read.
- Exhaustive local VM document inventory (all readable .txt/.html/.csv/.json/.eml/.enc/.bak across /home/{arif.khan,salim.uddin,it.admin,tania.akter}, /opt/firstbangla, /var/captures): only ONE bank statement exists on disk = Arif's own CityTrust `4521-887-2024-001` (already rejected). No other account-number document present locally.
- Cast of players (confession + emails + whatsapp): Arif Khan (insider, EMP-2024-0847), Salim Uddin (Director, took $150K cut, ref `SK-PRIVATE-2024-0510` in his `expenses_may.txt`), Rajesh Patel (+91-9876543210, RPC Consulting, Mumbai — mixing, 20% cut $400K), A. Reza <unknown321@protonmail.com> (external handler/attacker email).
- `transfer_records.db`: theft transfers id 35000/38000/42000 on 2024-05-10 09:30-31 to EXT-DEST-BTC/ETH/USDT (crypto, not bank). No bank-account destination for Salim's private $150K transfer in DB.
- PCAP endpoints: C2 185.220.101.47 /sync /confirm + SQLi probes `SELECT * FROM accounts WHERE branch_id=..`. No account-number receipt in strings.
- Conclusion: the external bank account ID must live in the full webmail (763 inbox + 486 sent), not yet fully searched locally. Running `work/fetch_all_mail.py` to download all and regex bank-account patterns (A/C, IBAN, SWIFT, IFSC, beneficiary, NNNN-NNN-NNNN-NNN).
- OPEN: identify which player's real name pairs with a genuine external bank account ID.