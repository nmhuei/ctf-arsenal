# Writeup: PhoneFarm

| Property | Value |
| :--- | :--- |
| **Category** | `Reverse` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `79` |

---

## 📝 Challenge Overview

Gần đây công an Đột kích "trang trại" 2.000 điện thoại ở Đà Nẵng: Chuyên "nuôi" tài khoản Zalo, Tinder ảo để phục vụ lừa đảo Campuchia. Đã thu được 1 phần mềm có tác dụng đổi thông tin thiết bị để gian lận. Qua quá trình khai thác đã biết một đối tượng tên luongvd đã crack phần mềm này. Tìm ra key của phần mềm mà không cần mua. Hãy tìm ra nó và chuyển sang dạng MD5

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Reverse`
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
