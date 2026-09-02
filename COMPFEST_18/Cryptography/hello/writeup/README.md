# Writeup: hello

| Property | Value |
| :--- | :--- |
| **Category** | `Cryptography` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `70` |

---

## 📝 Challenge Overview

```
hello! can you help me to recover the message?

Flag format is: flag[:-1] + "_" + sha256(flag[11:-1])[:16] + "}"
```

File đính kèm: `chall.sage` với hệ mật mã đại số trên vành thương đa thức $A = \mathbb{Z}_N[t] / (t^{10} - 2)$.

---

## 🔍 Phân tích & Quá trình giải

### 1. Tấn công Generalized Wiener Attack trên $e / N^{10}$
* Trong `chall.sage`:
  * $N = p \cdot q$ (2048-bit).
  * $\phi = (p^{10} - 1)(q^{10} - 1) = N^{10} - (p^{10} + q^{10}) + 1$.
  * Khóa bí mật $d$ được sinh nhỏ hơn ngưỡng $\approx \sqrt{N^5}$.
  * Khóa công khai $e \equiv (\phi - d)^{-1} \pmod \phi \implies e \cdot d \equiv -1 \pmod \phi \implies e d + 1 = k \phi$.
* Do $d$ nhỏ, phân số $\frac{e}{N^{10}} \approx \frac{k}{d}$ thỏa mãn định lý Legendre về liên phân số (Continued Fraction):
  $$\left| \frac{e}{N^{10}} - \frac{k}{d} \right| < \frac{1}{2d^2}$$
* Tìm các phân số hội tụ (convergents) của $\frac{e}{N^{10}}$, tại convergent thứ 3009 thu được $k, d$ và $\phi_{\text{candidate}}$.
* Giải phương trình bậc hai $X^2 - (N^{10} - \phi + 1)X + N^{10} = 0$ tìm được $p^{10}, q^{10}$, lấy căn bậc 10 thu được thừa số nguyên tố $p$ và $q$.

### 2. Cấu trúc nhóm nhân của vành thương $A = \mathbb{Z}_N[t] / (t^{10} - 2)$
* Xét đa thức $t^{10} - 2$ modulo $p$ và modulo $q$:
  * Modulo $p$: $2$ là thặng dư bậc 2 nhưng không phải bậc 5 (do $(2/p) = 1$ và $2^{(p-1)/5} \not\equiv 1$), nên $t^{10} - 2$ phân tích thành 2 đa thức bất khả quy bậc 5 ➔ Bậc của nhóm nhân modulo $p$ là $\lambda(p) = p^5 - 1$.
  * Modulo $q$: $q \equiv 3 \pmod 5$, căn bậc 5 của đơn vị có bậc 4 trên $\mathbb{F}_q$ ➔ Bậc của nhóm nhân modulo $q$ là $\lambda(q) = q^4 - 1$.
* Bậc lũy thừa toàn cục của vành:
  $$\lambda(N) = \text{lcm}(p^5 - 1, q^4 - 1)$$
* Khóa giải mã thực tế:
  $$d_{\text{true}} = e^{-1} \pmod{\lambda(N)}$$

### 3. Giải mã bản mã $c$
* Tính lũy thừa đa thức:
  $$m(t) \equiv c(t)^{d_{\text{true}}} \pmod{(t^{10} - 2, N)}$$
* Chuyển các hệ số $m_i$ thành các block byte và ghép lại thu được chuỗi bản rõ:
  `COMPFEST{c0ngr4tzzz_h3ngk3rrrr_g3n3r4l1Zed_w13n3R_4ttacK}`
* Ghép 16 ký tự đầu của sha256 phần nội dung flag theo đúng format yêu cầu.

---

## 💻 Script khai thác

Script giải mã hoàn chỉnh tại [`../solver/solve.py`](../solver/solve.py).

```bash
python3 solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `COMPFEST{c0ngr4tzzz_h3ngk3rrrr_g3n3r4l1Zed_w13n3R_4ttacK_f91f71b7c1b857d2}`
*(hoặc format `COMPFEST18{c0ngr4tzzz_h3ngk3rrrr_g3n3r4l1Zed_w13n3R_4ttacK_f91f71b7c1b857d2}`)*
