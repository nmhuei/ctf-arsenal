# Writeup: The 67th Line

| Property | Value |
| :--- | :--- |
| **Category** | `Cryptography` |
| **Points** | `100` |
| **Author** | `racoonhunter` |
| **Solves** | `46` |

---

## 📝 Challenge Overview

```
Old notes, short lines, and one sealed gate.

Start from:
@kuliah67.archive

Flag format:
COMPFEST18{64 lowercase hexadecimal characters + `_` + sha256(that 64 lowercase hexadecimal characters)[:16]}
```

---

## 🔍 Phân tích & Quá trình giải

### 1. OSINT & Giải mã Bacon Cipher trên Instagram
* Tìm thấy tài khoản Instagram `@kuliah67.archive` chứa 3 bài đăng với các khổ thơ 35 dòng mỗi bài.
* Chữ cái đầu mỗi dòng bắt đầu bằng `O` (Old, Only) hoặc `B` (Books, Beneath, Before, Between, Beyond).
* Mã hóa nhị phân 5-bit (O = 1, B = 0):
  * **Post 3 (cũ nhất):** `[17, 8, 18, 19, 4, 10, 26]` ➔ `RISTEK` + `.` (`ristek.`)
  * **Post 2:** `[11, 8, 13, 10, 27, 0, 18]` ➔ `LINK` + `/` + `AS` (`link/as`)
  * **Post 1 (mới nhất):** `[19, 4, 17, 6, 0, 19, 4]` ➔ `TERGATE` (`tergate`)
* Kết hợp lại thành shortlink: `https://ristek.link/astergate` ➔ Dẫn tới Google Drive folder chứa file `Archive.zip`.

### 2. Phân tích mật mã học (Zero-Sum Integral Cryptanalysis)
* File `chall.py` hiện thực một khối mật mã 3 vòng Feistel cải tiến trên 96-bit (12 bytes) với phép hoán vị bit tuyến tính và hàm phi tuyến $\_g$ bậc đại số 2.
* Tầng output cuối cho byte $i$: $C[i] = \text{matrix}(key[i] \gg 8) \cdot \_q(s_3[i]) \oplus (key[i] \& 255)$.
* Bậc đại số của 3 vòng nhỏ hơn số chiều của các không gian afin trong `records.json` ($d \in \{7, 8, 9\}$), do đó tổng XOR của trạng thái $s_3[i]$ trên mỗi tập afin bằng **0** ($\bigoplus s_3[i] = 0$).
* Phục hồi độc lập 12 bits trên ($m\_idx$) cho từng byte bằng brute-force $2^{12} = 4096$ ma trận.
* Dùng round key đã biết để chạy xuôi và tìm chính xác 8 bit mask còn lại từ bất kỳ cặp plaintext-ciphertext nào.

### 3. Mở khoá Sealed Gate
* Sử dụng 12 giá trị key hoàn chỉnh:
  `[208525, 781904, 786823, 634432, 351965, 1016321, 982026, 292426, 170007, 853094, 743427, 830957]`
* Giải mã `sealed.json` thành chuỗi 32-byte (64 hex characters) và tính toán sha256 16 ký tự đầu để tạo flag.

---

## 💻 Script khai thác

Script hoàn chỉnh tại [`../solver/solve.py`](../solver/solve.py) và bộ tăng tốc C tại [`../solver/solve.c`](../solver/solve.c).

```bash
python3 solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `COMPFEST18{5e9e8bf77207eca9c6906e80a57aa0e426f18ab8825a7b0f656cfa5d888a81c9_aefbd0dc566889bb}`
