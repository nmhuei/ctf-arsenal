# From Update To Encrypt - analysis
Ransomware forensics: user ran fake updater, update.exe encrypted 7 files (AES-256-GCM via BCrypt).

## Chain
- pcap: downloaded UpdateX7A91C.7z from 192.168.56.1:1337, update.exe GET /api/check -> {"campaign":"X7A91C","status":"ok"}
- sysmon: update.exe PID 2844 ppid explorer, 7 FileCreate .enc at 04:35:06, computer DESKTOP-7NNKNIK
- update.exe RE (r2+Ghidra): key = SHA256(lower(computer)|PID|campaign) = SHA256("desktop-7nnknik|2844|X7A91C")
- file format: magic "1337DaKL"(8) + tag(16) + ct; per-file 12B nonce via BCryptGenRandom, NOT stored, wiped after use
- nonces recovered from update.exe thread stack: mem.raw -> vol vadinfo --pid 2844 --dump (0xd30000 region), GHASH precompute + 1-AES-per-candidate scan
- hi.txt.enc decrypts (tag verified) to CSCV2026{c0rr3l4t3_b3f0r3_d3crypt}; ptit.txt decodes to Vietnamese decoy text; flag.jpeg decodes to photo (no visible flag)

## Candidate
- VERIFIED (local GCM tag verify + server "Correct"): CSCV2026{c0rr3l4t3_b3f0r3_d3crypt}
