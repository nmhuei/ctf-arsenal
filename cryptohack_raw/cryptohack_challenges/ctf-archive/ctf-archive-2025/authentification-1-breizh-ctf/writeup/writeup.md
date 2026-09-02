# Authentification 1 (Breizh CTF)

The application stores an authentication token as AES-GCM output in a cookie formatted as `ciphertext;tag`. The bug is nonce reuse plus weak verification behavior in the provided service.

Exploit chain:

1. Reset the challenge database/key with `/reset-db` when available.
2. Register and log in with a controlled long username, so the plaintext JSON is known: `{"username": "AAAA...", "role": "guest"}`.
3. Decode the Werkzeug-quoted cookie value and split it into ciphertext and tag.
4. XOR known plaintext with known ciphertext to recover the CTR keystream.
5. Build a target plaintext with role `super_admin`, encrypt it with the recovered keystream, and send any 16-byte tag because the vulnerable verifier ignores the failed integrity result.
6. Request `/admin` with the forged cookie to receive the flag.

Verified command:

```bash
python3 solve_authentification_live.py http://archive.cryptohack.org:61277
```
