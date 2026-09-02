# Secret Storage

| Property | Value |
| :--- | :--- |
| **Category** | `Crypto` |
| **Points** | `100` |
| **Solves** | 92 |

## 📝 Description

**Difficulty:** Hard  
**Author:** OddNorseman  

BrunnerCorp needed a new secret vault for their various needs, but license fees are too expensive nowadays! Thankfully, the intern had a ChatGPT Plus subscription, which is all they needed. Unfortunately the pentesters found the source code on a public GitHub along with an *encrypted vault export*, but that shouldn't be a problem... right? Oh and they phished one of the users. Here's their creds:

`maya.chen@brunnercorp.tld:Odense2026!`


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `crypto_secret-storage.zip` | `platform_attachment` | ✅ Downloaded | [crypto_secret-storage.zip](crypto_secret-storage.zip) |

## 🚩 Flag & Solution

- [x] Solved

```
brunner{but_th3_A1_s41d_1t_w45_f1n3???}
```

### Writeup / Notes

Attack: **AES-GCM nonce reuse via `import_vault`** (no key recovery needed).

1. App uses one `SECRET_ENCRYPTION_KEY` for BOTH secret encryption and the
   encrypted session cookie (AAD `secret/session/v1`).
2. Log in as `maya.chen@brunnercorp.tld:Odense2026!` (editor). Create a secret
   named `session/v1` with value `{"user_id":1,"role":"editor"}` → export vault →
   the ciphertext is a valid admin session cookie (user_id 1 = admin).
3. As admin, call `/api/v1/vault/import` with a fake "Flag" secret: same nonce as
   the real flag, value `aaaa...`, encrypted with an arbitrary key (e.g. 32×`0x01`),
   AAD `secret/Flag`. The server decrypts it with OUR key then re-encrypts it with
   THE SERVER key but **reuses the flag's nonce**.
4. Re-export the vault → now have the fake plaintext encrypted with the flag's
   keystream. XOR: `flag = enc_flag XOR fake_plaintext XOR reexported_ciphertext`.

Reference: clairelevin writeup (github.com/clairelevin/clairelevin.github.io,
`_posts/2026-08-28-secret-storage.markdown`).
