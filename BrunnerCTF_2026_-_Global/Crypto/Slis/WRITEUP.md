# Writeup: Slis (BrunnerCTF 2026 - Global)

- **Challenge**: Slis
- **Category**: Crypto
- **Difficulty**: Easy-Medium
- **Points**: 100
- **Path**: `/home/light/Workspace/CTF/BrunnerCTF_2026_-_Global/Crypto/Slis`
- **Status**: ✅ SOLVED
- **Flag**: `brunner{Pease_porridge_sHOrT_:)}`

---

## 1. Challenge Overview

The challenge provides a Python script `slis.py` packaged inside `crypto_slis.zip`:

```python
flag = "brunner{" + input() + "}"
n = int.from_bytes(flag.encode())
lis = [n//(i+2) - n//(i+3) for i in range(9**5)]
assert sum(lis) == 22263691028918788395010325066307464924652601045336492930678310479674861811846
```

Given:
- Total sum $S = 22263691028918788395010325066307464924652601045336492930678310479674861811846$.
- Range length: $9^5 = 59049$.
- Flag format: `brunner{...}`.

---

## 2. Mathematical Analysis: Telescoping Sum

Examining the list comprehension:
$$\text{lis} = \left[ \lfloor \frac{n}{i+2} \rfloor - \lfloor \frac{n}{i+3} \rfloor \right] \quad \text{for } i \in [0, 9^5-1]$$

Summing over all $i$:
$$S = \sum_{i=0}^{59048} \left( \lfloor \frac{n}{i+2} \rfloor - \lfloor \frac{n}{i+3} \rfloor \right)$$

Expanding terms:
- For $i = 0$: $\lfloor \frac{n}{2} \rfloor - \lfloor \frac{n}{3} \rfloor$
- For $i = 1$: $\lfloor \frac{n}{3} \rfloor - \lfloor \frac{n}{4} \rfloor$
- For $i = 2$: $\lfloor \frac{n}{4} \rfloor - \lfloor \frac{n}{5} \rfloor$
- ...
- For $i = 59048$: $\lfloor \frac{n}{59050} \rfloor - \lfloor \frac{n}{59051} \rfloor$

Since intermediate terms cancel out identically:
$$S = \lfloor \frac{n}{2} \rfloor - \lfloor \frac{n}{59051} \rfloor$$

---

## 3. Solution Strategy

Because $f(n) = \lfloor \frac{n}{2} \rfloor - \lfloor \frac{n}{59051} \rfloor$ is monotonically non-decreasing:
1. Binary search over $[0, 10^{100}]$ to find $n$ satisfying $f(n) = S$.
2. Decode $n$ to bytes: `int.to_bytes(...)`.

Flag recovered:
`brunner{Pease_porridge_sHOrT_:)}`
