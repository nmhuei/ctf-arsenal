# Writeup: save the water

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `484` |
| **Author** | `uje` |
| **Solves** | `5` |

---

## 📝 Challenge Overview

```
My AI agent is running slowly; it keeps loading and never finishes

WARNING: THE ATTACHMENT FOR THIS CHALLENGE CONTAINS ACTIVE AND HIGHLY DANGEROUS MALWARE!
IT IS STRICTLY PROHIBITED TO EXECUTE OR RUN THE FILE OUTSIDE A SECURE ISOLATION ENVIRONMENT!
```

Dịch vụ tương tác: `nc 34.2.147.230 7000` gồm chuỗi 11 câu hỏi phân tích Forensic mạng, mã độc và bộ nhớ.

---

## 🔍 Phân tích chi tiết 11 câu hỏi

### Question 1: What is the IP Address of the victim?
- Phân tích PCAP bằng Wireshark/tshark: Gói tin PowerShell khởi tạo kết nối tải payload từ máy chủ `192.168.100.20`.
- **Đáp án**: `192.168.100.10`

### Question 2: Versioning artifact exposed in the very first phase?
- Kiểm tra header `User-Agent` của request HTTP đầu tiên: `Mozilla/5.0 ... WindowsPowerShell/5.1.26100.8521`.
- **Đáp án**: `5.1.26100.8521`

### Question 3: First 4 magic bytes in hex to authenticate connection?
- Stream TCP 0 (port 4444): Gói tin đầu gửi `deadbeef_AUTH_SUCCESS`.
- Format `xx-xx-xx-xx`.
- **Đáp án**: `de-ad-be-ef`

### Question 4: 32-bit SSRC tracking the multimedia datagram stream?
- Phân tích luồng RTP/RTCP trên UDP port 1234/1235: SSRC trong header là `0x82e7d63a`.
- Chuyển sang decimal: `2196231738`.
- **Đáp án**: `2196231738`

### Question 5: Secret string hidden in timing covert channel?
- Phân tích 281 gói ICMP Echo Request với `ident == 9999` (dữ liệu `BEACON`):
  - Độ trễ giữa các gói là ~1.0 giây (`0`) hoặc ~2.0 giây (`1`).
  - Giải mã chuỗi bit thành chuỗi ASCII 34 ký tự: `d0nt_ruN_th3_m4lw4r3_y4hh_82117caa`.
- **Đáp án**: `d0nt_ruN_th3_m4lw4r3_y4hh_82117caa`

### Question 6: MD5 checksum of reconstructed massive payload?
- Ghép chuỗi mật khẩu cho `private.676767`: `d0nt_ruN_th3_m4lw4r3_y4hh_82117caa512de1cc679e2acb37092e10a6111c22`.
- Giải nén `private.676767` thu được `fastAI.zip`.
- Trích xuất 32,221 gói ICMP Echo Request (`ident == 1337`), loại bỏ tiền tố 5 byte `EXFIL` ở đầu mỗi gói để thu được tệp Windows Minidump `memory.dmp` hoàn chỉnh (45,109,394 bytes).
- Tính MD5 của `memory.dmp`: `c61e123e24a6025bc1aac86391385070`.
- **Đáp án**: `c61e123e24a6025bc1aac86391385070`

### Question 7: AES Key and IV string in memory?
- Tìm kiếm cấu trúc `PyBytesObject` trong `memory.dmp`:
  - Khóa AES (32 bytes): `bd7bf788d62bdec9c219316da4487314`
  - IV (16 bytes): `y0u_g0t_tr4pp3d!`
  - Giải mã `video.enc` (AES-CBC) thành công thu được `video.zip` chứa `video.mp4`.
- **Đáp án**: `bd7bf788d62bdec9c219316da4487314_y0u_g0t_tr4pp3d!`

### Question 8: Multi-digit authorization code on evidence?
- Xem các frame trong `video.mp4`: Người trong video cầm tờ giấy viết dãy số `16031115`.
- **Đáp án**: `16031115`

### Question 9: SHA256 hash value of the malware?
- Dùng mật khẩu `16031115` để giải nén `fastAI.zip`, thu được `fastloader.exe` (74,408,861 bytes).
- Tính SHA256: `be69c8c00b73aadbb26ca44707ec1d489f891d2e848dd7e834b8f881bcdeb33d`.
- **Đáp án**: `be69c8c00b73aadbb26ca44707ec1d489f891d2e848dd7e834b8f881bcdeb33d`

### Question 10: Hexadecimal values of starting Offset and data block Size?
- Phân tích PE Header của `fastloader.exe`: Phần overlay NSIS bắt đầu tại `0x00009600` với kích thước `0x046ecd9d`.
- **Đáp án**: `00009600_046ecd9d`

### Question 11: Original developer of privilege escalation utility?
- Trích xuất file nén NSIS `fastloader.exe` ➔ `app-64.7z` ➔ `resources/elevate.exe`.
- Đọc thông tin PE Version Info của `elevate.exe`: `CompanyName: Johannes Passing`.
- **Đáp án**: `Johannes_Passing`

---

## 💻 Script tự động giải

Script tự động tương tác socket và lấy cờ tại [`../solver/solve.py`](../solver/solve.py).

```bash
python3 solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `COMPFEST18{b0r05_41r_vv0y_j4n64n_p3cu7_p3cu7_41_mu1u_dfmabfbfdadf}`
