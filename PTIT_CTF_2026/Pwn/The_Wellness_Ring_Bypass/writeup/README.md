# Writeup: The Wellness Ring Bypass

| Property | Value |
| :--- | :--- |
| **Category** | `Pwn` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `33` |

---

## 📝 Challenge Overview

Để chuẩn bị cho cuộc thi Pwn2Own Ireland 2026, nhh và vietnq đã chốt hạ mục tiêu là chiếc nhẫn thông minh Oura Ring 5, một thử thách hoàn toàn mới. Tuy nhiên khi debug firmware và dùng đủ mọi thủ thuật fuzzing cả tuần vẫn không thấy crash. Bạn hãy giúp 2 anh chàng này tìm bug và khai thác chiếc nhẫn này nhé!

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Pwn`
- Key observations & vulnerability hypothesis:
  *(Document reverse engineering, source code review, or protocol analysis here)*

---

## 💻 Exploitation Strategy & PoC

Exploit script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

---

## 🚩 Flag

- Status: `- [ ] Solved`
- Flag: `FLAG{...}`
