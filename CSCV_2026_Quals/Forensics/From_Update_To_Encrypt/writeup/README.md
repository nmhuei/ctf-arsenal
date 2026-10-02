# Writeup: From Update To Encrypt

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `133` |

---

## 📝 Challenge Overview

> Ring... tuttt... tuttt...
> 
> SOC: Alo, Vũ ấy hả em.
> 
> VuVT: Anh ơi, em chỉ chạy update thôi mà sao máy em tự nhiên bị mã hóa rồi...
> 
> SOC: Đừng động vào máy nữa. Bọn anh sẽ kiểm tra.

Một bộ dữ liệu được thu thập từ máy tính gặp sự cố.

Hãy điều tra xem chuyện gì đã thực sự xảy ra và tìm ra thông tin cần thiết để khôi phục kết quả cuối cùng.

-------------
> Ring... tuttt... tuttt....
> 
> SOC: Moshi moshi, Is that you Vu?
> 
> VuVT: Holy moly, I've just running some kind of updates and now my device got encrypted.
> 
> SOC: Do not touch your keyboard. We'll come and investigate

Then a data sample was collected from the incident

Investigate to figure it out what happened and find the information to restore the final results.

Download [here](https://drive.google.com/file/d/1g2-1Jy7pMjjvWO2WmLAUDkUidB3h9iSp/view?usp=sharing)

---

## 🔍 Reconnaissance & Vulnerability Analysis

- Target Connection: `-`
- Category: `Forensics`
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

- Status: `- [x] Solved`
- Flag: `CSCV2026{c0rr3l4t3_b3f0r3_d3crypt}`
