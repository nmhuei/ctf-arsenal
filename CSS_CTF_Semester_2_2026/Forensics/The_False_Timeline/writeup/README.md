# The False Timeline - Writeup

## Rationale
The description claimed KAI-7 performed the emergency export at 03:17, but also stated KAI-7 had already disconnected. The goal was to reconstruct the real timeline and recover the encrypted key.

## Discovery trail
1. Decompressed `nexus_relay.img.xz` and identified an ext4 filesystem.
2. Inspected filesystem contents with `debugfs` because direct mounting was unavailable.
3. Found relevant artifacts:
   - `/var/log/nexus/relay.log`
   - `/var/log/audit/audit.log`
   - `/var/cache/nexus/.ekey-cache`
   - `/opt/nexus/lib/exporter.py`
4. The logs showed KAI-7's SSH session ended at 03:05:41, while a later service account `svc-relay` executed `nx-export --emergency`.
5. `exporter.py` revealed the AES-GCM key derivation:

`sha256(machine_id|session_uuid|event_epoch)`

6. Extracted machine id and session data from the filesystem. The valid export context was the `svc-relay` session UUID and the audit event epoch `4157543568`.
7. Decrypted `.ekey-cache` and recovered the flag.

## Result
`CSSCTF{kai_did_not_do_it}`
