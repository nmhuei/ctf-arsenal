# Verilicious (Cyber Apocalypse 2025)

The challenge exposes RSA PKCS#1 v1.5 encryption plus a padding-validity verifier. The existing `solve_online.py` is a Bleichenbacher adaptive chosen-ciphertext skeleton.

Exploit idea:

1. Import the public key and ciphertext from the attachments.
2. Implement `oracle(ct)` so it talks to the real remote verifier and returns whether PKCS#1 v1.5 padding is accepted.
3. Run the standard Bleichenbacher interval attack: find valid multipliers `s`, maintain the interval set for the plaintext, and shrink it until one integer remains.
4. Strip the PKCS#1 v1.5 padding bytes to recover the flag.

Current status: the repository contains the attack skeleton, but the target host/port and oracle parsing are placeholders, so no verified flag was recovered in this session.
