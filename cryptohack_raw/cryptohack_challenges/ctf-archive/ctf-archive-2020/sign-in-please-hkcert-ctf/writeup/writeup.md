# Sign in Please (HKCERT CTF)

The server lets us query a `spy` command with chosen permutation boxes and salts. The password is hidden inside a SHA-256 construction, but the permutation oracle allows recovering it two characters at a time.

Exploit chain:

1. Query `spy` with an identity pbox and fixed salt to get a base SHA-256 compression state.
2. Precompute a rainbow table for all two-character base64 alphabet pairs appended to that state.
3. For each password pair, craft a pbox that positions two unknown password bytes into the final compression block while fixing the remaining bytes.
4. Match the returned digest in the rainbow table to recover the password pair.
5. Request the auth challenge, compute the correct digest with the recovered password and server-provided salt/pbox, and submit it.

Verified command:

```bash
python3 solve_remote.py archive.cryptohack.org 1024
```
