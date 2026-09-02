# Chronofault

| Property | Value |
| :--- | :--- |
| **Category** | `forensics` |
| **Points** | `156` |
| **Author** | fg0x0 |
| **Solves** | 114 |

## 📝 Description

Somebody walked a projected service token out of the `commons-core`
namespace and pulled the parity OTP secret. Four megabytes left for an
off-register host, and the pairing rotation ran an hour late.

Our on-call analyst already closed this. He sorted every log by its
timestamp, found the session that touched `/api/v1/ledger/issue` a tenth of
a second before the core accepted a role header, and named a contractor.

The contractor's counterpart filed a chronyc dump in her defence. The DMZ
segment has not reached an NTP server since the firewall change. Two of
these five hosts have been free-wheeling on their RTC for twelve days, and
one of them stamps the log our analyst sorted by.

A timeline is an accusation. Rebuild this one properly, then open the
escrow with `unlock.py`.

> [!CONNECTION]
> https://chronofault-qnebgbco.challenge.2026.haruulzangi.mn/artifact.zip


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `attachment` | `description_direct_file` | ❌ Failed | [https://chronofault-qnebgbco.challenge.2026.haruulzangi.mn/artifact.zip](https://chronofault-qnebgbco.challenge.2026.haruulzangi.mn/artifact.zip) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
