# Writeup: Mid

| Property | Value |
| :--- | :--- |
| **Category** | `Misc` |
| **Points** | `181` |
| **Author** | `Walker` |
| **Solves** | `84` |

---

## 📝 Challenge Overview

The challenge presents a guessing game where we need to find a 30-character password generated from `string.digits + string.ascii_letters` (62 possible characters per position).
- Total search space: $62^{30} \approx 5.91 \times 10^{53} \approx 2^{178.63}$.
- Max queries allowed: 195 queries.
- At each query, we provide `<state> <guess>`.
- A hidden variable `switch_at` is chosen uniformly at random in $\{0, 1, \dots, 195\}$.
- Before query `switch_at`, `mood = 0`. At and after `switch_at`, `mood = 1`.
- If `state == mood`: the oracle provides truthful comparison feedback: `"smaller"` if `guess < password`, `"larger"` if `guess > password`, or `"equal"` (which prints the flag).
- If `state != mood`: the oracle returns a uniformly random coin flip `secrets.choice(("smaller", "larger"))`.

---

## 🔍 Vulnerability & Information Analysis

1. **Information Theoretic Bound**:
   - Recovering a $62^{30}$ state requires $\lceil \log_2(62^{30}) \rceil = 179$ bits of truthful comparison feedback.
   - We are given 195 queries, leaving exactly $195 - 179 = 16$ spare queries.

2. **Phase Transition Alignment**:
   - `switch_at` is chosen uniformly in $[0, 195]$.
   - The probability that `switch_at <= 16` is:
     $$P(\text{switch\_at} \le 16) = \frac{17}{196} \approx 8.67\%$$
   - When `switch_at <= 16`, `mood` switches to 1 on or before query 16 and stays 1 for the entire rest of the session.
   - If we send `state = 1` across the session:
     - For the first 16 queries, the oracle may be lying if `switch_at > 0`. We can simply burn these 16 queries with dummy inputs (e.g. `1 0`).
     - Once query 16 has passed, if `switch_at <= 16`, `mood` is guaranteed to be 1 for all remaining 179 queries!
     - Therefore, from query 16 to 194 (179 queries total), `state == mood` is guaranteed to hold 100% of the time.

3. **Exact Global Binary Search**:
   - Over the space of integers $[0, 62^{30} - 1]$, mapping bijectively to base-62 strings of length 30:
   - Exactly $\lceil \log_2(62^{30}) \rceil = 179$ queries of truthful binary search pinpoint the exact password with zero errors.
   - In expectation, running trials takes $\approx \frac{1}{0.0867} \approx 11.5$ connection attempts.
   - Locally, each trial executes in $\sim 0.03$s, solving the challenge in under 0.6 seconds!

---

## 💻 Exploitation Strategy & PoC

Solver script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

### Execution Output:
```text
[*] Starting solver for challenge Mid...
[*] Target: local script /home/light/Workspace/CTF/TFC_CTF_2026/Misc/Mid/challenge/chall.py
[*] Attempt 10... waiting for trial with switch_at <= 16
[+] SOLVED on attempt 17 in 0.59s!
[+] FLAG: TFCCTF{no1_s0_3asy}
[+] Flag written to /home/light/Workspace/CTF/TFC_CTF_2026/Misc/Mid/flag.txt
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `TFCCTF{no1_s0_3asy}`
