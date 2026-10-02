# Signed, Sealed, Subverted

| Property | Value |
| :--- | :--- |
| **Category** | `RE` |
| **Points** | `500` |
| **Solves** | 0 |

## 📝 Description

## Scenario

A medical gateway receives a firmware update — the manifest is validly signed. After install, a module appears that was never in the manifest. No signature forgery, no race condition, no memory bug. So why is what gets installed different from what was verified?

Create a minimal poc.upd to prove it. The runner checks: correct module, correct nonce, integrity tree intact.

## Provided files

- `updater-aarch64`
- `boot.qcow2`
- `manifest.cddl`
- `signed-base.upd`
- `public-keys.cbor`
- `runner.sh`
- `policy.txt`
- `SHA256SUMS`

## Submission

`runner.sh poc.upd`

Download [here](https://drive.google.com/file/d/1blbxI3xCeZZssh637YnTqZ-fOj3o650_/view?usp=sharing)


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `here` | `description_gdrive` | ✅ Downloaded | [here](here) |

### 🔗 External Links in Description

- [here](https://drive.google.com/file/d/1blbxI3xCeZZssh637YnTqZ-fOj3o650_/view?usp=sharing) (`gdrive`)

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
