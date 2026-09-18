# Echoes

| Property | Value |
| :--- | :--- |
| **Category** | `Hardware` |
| **Points** | `500` |
| **Solves** | 0 |
| **Tags** | `Hardware` |

## 📝 Description

Two [chips](/tasks/Echoes_a6abb166d71df1315e611540520dde97d6811a75.txz) tried to talk at once. Now their argument is your problem.

**Hint:** Echoes do not speak one segment at a time.

The three PRBS reference intervals reveal a five-step history in the analog signal. Use this learned model to decode the two unknown intervals as a path through four states:

`NONE, A, B, and AB`

When you have stream candidates, bind them with:

stream_a + stream_b + public_nonce

Then verify the HMAC tag stored in `eeprom.bin`.

All required files are already provided: `session.ecap`, `transaction.json`, and `eeprom.bin`.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `Echoes_a6abb166d71df1315e611540520dde97d6811a75.txz` | `platform_attachment` | ✅ Downloaded | [Echoes_a6abb166d71df1315e611540520dde97d6811a75.txz](Echoes_a6abb166d71df1315e611540520dde97d6811a75.txz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
