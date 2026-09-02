# cyclotomic-echo

| Property | Value |
| :--- | :--- |
| **Category** | `crypto` |
| **Points** | `172` |
| **Author** | afish |
| **Solves** | 43 |

## 📝 Description

Some keys disappear. Their geometry does not.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `crypto_cyclotomic-echo.tar.gz` | `platform_attachment` | ✅ Downloaded | [crypto_cyclotomic-echo.tar.gz](crypto_cyclotomic-echo.tar.gz) |

## 🚩 Flag & Solution

- [x] Solved

```
zdk{cyc10T0mic_eCho_on3_BA5IS_biNdS_3verY_TeAM_ARcHIvE}
```

### Writeup / Notes

The handout `recovery.json` leaks the exact private NTRU-style basis `(f,g,F,G)`
with `fG − gF = 1` behind the public Hermitian form `Q = B·B*` over
`Z[x]/(x^128+1)`. Forging reduces to parity-coset reduction: map the hash point
`(x,y)` through `B`, reduce coefficients mod 2, map back through the integral
`B⁻¹`, and submit `s1 = (y−e1)/2`. Norm 133 ≤ bound 16384. No lattice reduction
needed. Full solver + verification in `scratch/ctf-workspaces/cyclotomic-echo/`.
