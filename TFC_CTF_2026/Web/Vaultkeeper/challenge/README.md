# Vaultkeeper

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `319` |
| **Author** | skyv3il |
| **Solves** | 32 |
| **Tags** | `BABY`, `container`, `http` |

## 📝 Description

Self-hosted backup & restore appliance,schedule snapshots, ship them anywhere,roll a site back


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `vaultkeeper-source.zip` | `platform_attachment` | ✅ Downloaded | [vaultkeeper-source.zip](vaultkeeper-source.zip) |

## 🚩 Flag & Solution

- [ ] Remote flag recovered (local chain verified)

```
FLAG{...}
```

### Writeup / Notes

The exploit chain is validated against a fresh local Docker appliance built from the supplied
source. The remote instance currently returns Apache `403 Forbidden` for the loopback-only
SSRF/keyring/unseal endpoints, so no remote competition flag is recorded.
