# WrongCube+ — solve notes

## What this challenge is
- Competition: **Junior Crypt 2026 CTF** (GRODNO::CTF, Hrodna State University, SPCS),
  platform GZCTF at http://ctf-spcs.mf.grsu.by/ (game id=2, "Junior Crypt 2026 CTF").
- Author: @vvanuss. Category: Reverse. Points: 923.
- The "External Link" attachment is actually the download for `WrongCube+.exe` (~37 MB,
  PyInstaller PyQt6 app + native `wrongkube_validator.dll`) — the platform hosts attachments
  externally, hence "External Link" in the UI. The description's "utility for visualizing
  Kubernetes clusters online" is flavor for the K8s-cluster-setup puzzle app.
- This is the first of a 3-part series: WrongCube+ / WrongCube++ / WrongCube+++.

## Source of the solution (writeups found)
- https://github.com/cyb3rkn1ght-tdtu/Writeups/blob/main/Junior.Crypt.2026/Reverse_Engineering/Wrongkube%2B.md
  (full analysis: pyinstxtractor → validator_bridge.pyc → wrongkube_validator.dll; flag decryption
  loop at 0x180005390 is fully independent of puzzle input; static 46-byte array at 0x18002bf00)
- https://github.com/sam-in07/IIUC_x86_writeups/blob/saminnn/Asia_Bloc/Russian/Junior_Crypt_2026_CTF/reverse/WrongCube_plus.md
  (matches our exact challenge description; writeup body was left empty)
- Series writeups: Wrongkube++.md / Wrongkube+++.md in the same cyb3rkn1ght repo
  (flags of later parts differ — not ours).

## Verification
Re-implemented the decryption loop from the writeup (constants + 46-byte array) in Python
and ran it — output byte-for-byte: `grodno{5h4d0w_c0ntr0l_pl4n3_qu0rum_r3c0nc1l3d}`.
Flag is 46 bytes, matches `grodno{...}` format.

## Timestamps
- Searched/fetched: 2026-08-06
