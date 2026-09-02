# Payphone

| Property | Value |
| :--- | :--- |
| **Category** | `pwn` |
| **Points** | `656` |
| **Author** | flame |
| **Solves** | 9 |

## 🔌 Connection / Service
- URL: [https://payphone-gige4buw.challenge.2026.haruulzangi.mn](https://payphone-gige4buw.challenge.2026.haruulzangi.mn)

## 📝 Description

Make a call and listen closely.

Run `/flag` to get the flag.

Payphone places the call, so you need somewhere for it to call: a
publicly reachable TCP listener of your own.

Payphone holds the key to the real challenge, use it to decrypt the transmission:

```sh
PAYPHONE_BUNDLE_KEY='' openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -md sha256 -pass env:PAYPHONE_BUNDLE_KEY -in payphone-binaries.tar.zst.enc -out payphone-binaries.tar.zst
tar --use-compress-program=unzstd -xf payphone-binaries.tar.zst
```

> [!CONNECTION]
> https://payphone-gige4buw.challenge.2026.haruulzangi.mn


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `pwn_payphone.tar.gz` | `platform_attachment` | ✅ Downloaded | [pwn_payphone.tar.gz](pwn_payphone.tar.gz) |

### 🔗 External Links in Description

- [https://payphone-gige4buw.challenge.2026.haruulzangi.mn](https://payphone-gige4buw.challenge.2026.haruulzangi.mn) (`generic_url`)

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
