# Ghost Dependency

| Property | Value |
| :--- | :--- |
| **Category** | `RE` |
| **Points** | `500` |
| **Solves** | 0 |

## 📝 Description

## Scenario

A Rust warehouse manager agent — valid signature, clean SPDX, green CI. But on exactly one server, the build silently exfiltrates a token. Everything matches when you look at package names. The problem is elsewhere.

Find the component that entered the build, identify the target server, and reproduce the activation condition.

## Provided files

- `warehouse-agent`
- `agent.spdx.json`
- `cargo-build.log`
- `registry.tar.zst`
- `flag.enc`
- `verify.py`
- `FORMAT.md`
- `SHA256SUMS`

## Submission

`verify.py proof.json`


Download [here](https://drive.google.com/file/d/170rHz-PX3XnwdtCSIoB3uBSbKKJXkEXk/view?usp=sharing)


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `here` | `description_gdrive` | ✅ Downloaded | [here](here) |

### 🔗 External Links in Description

- [here](https://drive.google.com/file/d/170rHz-PX3XnwdtCSIoB3uBSbKKJXkEXk/view?usp=sharing) (`gdrive`)

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
