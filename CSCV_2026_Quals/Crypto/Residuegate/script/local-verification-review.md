# Tổng hợp kiểm chứng local — 2026-09-25

Trạng thái: **chưa giải được, chưa có flag thật được xác minh**. Báo cáo này chỉ tổng hợp dữ liệu tĩnh và phép tính offline. Không chạy solver cũ, không kết nối dịch vụ, không kiểm tra bộ nhớ tiến trình trong lần đối chiếu này.

## 1. Đối chiếu skill ctf-crypto

Nguồn yêu cầu: `/home/light/.agents/skills/ctf-crypto/SKILL.md`.

| Yêu cầu | Bằng chứng hiện có / phần thiếu |
| --- | --- |
| Giữ evidence trong workspace riêng | Có archive, binary, metadata, cache và các mẫu JSON đã lưu. |
| Đọc attack-router, phân loại từ cấu trúc, chạy kiểm tra phân biệt rẻ | Đã đọc router và orchestration trong bước tiếp theo; kiểm tra được lớp classifier. Chưa hoàn tất phân loại và kiểm chứng toàn bộ cấu trúc mật mã. |
| Mô hình toán rõ tham số, đơn vị, quy ước modulo | Có phép tính classifier; chưa có mô hình đầy đủ được kiểm chứng cho toàn bộ bài. |
| Đọc lattice workflow trước LLL/BKZ | Có thí nghiệm lịch sử liên quan lattice; chưa có bằng chứng đáp ứng quy trình bắt buộc trước khi chạy. |
| Solver tái lập, kiểm tra mọi ứng viên với dữ liệu gốc | Chưa đạt. `solver/solve.py` không xác minh toàn bộ điều kiện challenge. |
| Nếu chuyển chuyên gia: math_workspace riêng, handoff thuần toán, validator | Chưa xác minh có bộ handoff đạt chuẩn. Đây là yêu cầu khi cần chuyển chuyên gia, không phải mọi bài đều bắt buộc gọi chuyên gia. |
| Khi dùng chuyên gia: agy mặc định; Astra chỉ sau handoff hợp lệ | Chưa có bằng chứng đã thực hiện đúng bước này. Chưa gọi thêm công cụ hoặc agent trong lần đối chiếu. |
| Kết luận bằng verifier độc lập và đầy đủ | Chưa đạt. Một vector có vẻ đúng hoặc flag đọc từ cấu hình không đủ. |

Kết luận tuân thủ: **chưa đầy đủ**. Không thể sửa thiếu sót này chỉ bằng đổi tên script hoặc đánh dấu báo cáo `passed`.

## 2. Bộ dữ liệu và chương trình được cung cấp

- `challenge/give_to_player/local-server/residuegate-hard`: ELF x86-64, PIE, dynamically linked, stripped. Build ID: `6b2f7250131514023c51b13934cf9eb0895916ef`.
- Dockerfile dùng Debian bookworm-slim, sao chép binary có sẵn, chạy với UID 10001 và `PORT=5000`. Docker build này đóng gói binary; không biên dịch lại source.
- Không thấy source server trong danh sách tệp được cung cấp. Vì vậy chưa có cơ sở khẳng định một server tự viết lại tương đương server gốc.
- Compose gắn `local-data` read-only vào `/data/badges`, cung cấp đường dẫn manifest/cache và expected count bằng 1. Filesystem container read-only, có tmpfs cho `/tmp`.
- Manifest chứa `base_badge.png`. Metadata khai báo kích thước ảnh 32 × 32.
- `FLAG` trong Compose là `CTF{local_test_only}`. `flag.txt` hiện trùng đúng giá trị này; đó là fixture.

## 3. Kiểm tra toàn vẹn đã chạy lại

| Tệp | SHA-256 | Kết quả |
| --- | --- | --- |
| `qwen_cache.bin` | `2b2cb0b78ddf017dff1c0c36715025b7669fae839aad221b9c7b371ed6a46523` | Khớp `binary_sha256` trong metadata |
| `manifest.txt` | `61c7a729ff2740142faa7c1d4fad9be6aadd1e7b6913ef9c0f16a2d954138832` | Khớp `manifest_sha256` trong metadata |

Hai hash này kiểm tra tính nhất quán với metadata được cung cấp, không phải chứng thực nguồn phát hành. `binary_sha256` ở đây là hash cache binary, không phải ELF server.

## 4. Layout cache và phép tính đã kiểm chứng

Cache dài 744 byte. Magic 8 byte là `RGQWEN1\0`. Phần còn lại dài 736 byte, phù hợp với cấu trúc đang dùng:

`32 byte đầu + 16 × (32 byte opaque + 12 byte embedding) = 736 byte`.

Vai trò ngữ nghĩa của những trường 32 byte chưa được xác minh lại trong đợt này. Không nên suy ra chúng là khóa hay seed từ độ dài.

Mỗi tọa độ embedding được đọc là **int8 có dấu**. Với ma trận W kích thước 4 × 12 và bias b lấy nguyên từ `qwen_cache.json`:

`logit[c] = b[c] + Σ W[c,j] × embedding[j]`, với `j = 0..11`.

`top = argmax(logit)` và `margin = logit_lớn_nhất − logit_lớn_thứ_hai`.

Tính lại bằng số nguyên Python cho kết quả sau; chỉ số variant và class đều bắt đầu từ 0:

| Variant | Logits | Top | Margin |
| --- | --- | --- | --- |
| 0 | [59, -102, 308, 40] | 2 | 249 |
| 1 | [89, -89, 323, 17] | 2 | 234 |
| 2 | [109, -62, 173, 172] | 2 | 1 |
| 3 | [100, -117, 238, 88] | 2 | 138 |
| 4 | [92, -51, 144, 150] | 3 | 6 |
| 5 | [91, -45, 197, 84] | 2 | 106 |
| 6 | [76, -75, 156, 168] | 3 | 12 |
| 7 | [96, -62, 253, 132] | 2 | 121 |
| 8 | [89, -60, 180, 78] | 2 | 91 |
| 9 | [67, -42, 248, 40] | 2 | 181 |
| 10 | [72, -108, 161, 47] | 2 | 89 |
| 11 | [90, -98, 223, 87] | 2 | 133 |
| 12 | [64, -70, 162, 148] | 2 | 14 |
| 13 | [102, -85, 196, -8] | 2 | 94 |
| 14 | [53, -56, 178, 85] | 2 | 93 |
| 15 | [66, -128, 191, 28] | 2 | 125 |

Metadata đặt `required_margin=12`. Nếu kiểm tra điều kiện class 3 và margin ≥ 12 của script cũ thì chỉ variant 6 đạt. Điều này chỉ đúng cho cache được cung cấp và điều kiện nói trên; chưa chứng minh nghiệm đầy đủ của session.

## 5. Pipeline vision được khai báo, chưa tái lập đầy đủ

Nguồn: `qwen_cache.json` và bản lưu `script/objective.json`.

- Backbone được khai báo: Qwen3-VL-2B-Instruct; revision `89644892e4d85e24eaac8bacfd4f463576704203`.
- Xử lý RGB, resize bicubic 448 × 448, lấy trung bình image tokens cuối bằng float32.
- Feature 2048 chiều được chiếu xuống 12 chiều rồi lượng tử hóa về khoảng [-16,16].
- Công thức lượng tử hóa được khai báo: `clip(rint((projected-center)/scale*gain), -16, 16).astype(int8)`, gain bằng 8.
- Metadata cache ghi torch `2.8.0+cu128`; objective lưu runtime torch `2.8.0+cpu`. Đây là khác biệt metadata cần lưu ý khi so sánh tái lập, không tự nó chứng minh có lỗi.
- Kiểm chứng được classifier từ embedding có sẵn không đồng nghĩa đã tái lập image → embedding. Chưa chạy lại backbone hoặc so sánh từng bước float32 trong đợt này.

Để tối ưu kiểm chứng, kiểm tra hash/layout trước, sau đó embedding → logits, rồi mới đến pipeline ảnh tốn tài nguyên. Ghi riêng sai khác float và sai khác sau lượng tử hóa; gần ngưỡng làm tròn, sai khác nhỏ có thể đổi int8.

## 6. Objective đầy đủ khác với kiểm tra một variant

Hai tệp lưu `script/objective.json` và `script/remote_objective.json` có nội dung JSON bằng nhau tại thời điểm kiểm tra. Điều này chỉ nói về các bản lưu, không khẳng định trạng thái dịch vụ hiện tại.

Objective mô tả commitment cho sáu slot, mỗi slot có 16 biến thể; không gian tuple là `16^6 = 16,777,216`. Một variant có class/margin đạt ngưỡng trong cache không đủ để xác nhận objective này.

Session local đã lưu có các trường base_image_slots, combination, crypto, expires_at, limits, mixing_matrix, model và session_id. Mô tả schema hay thí nghiệm trên một session chưa chứng minh xử lý đúng mọi session hoặc server chấp nhận kết quả.

Các thí nghiệm mật mã và truy vết trước đây chỉ là artifacts lịch sử; chưa có bằng chứng end-to-end đầy đủ. Báo cáo này không cung cấp lại quy trình khai thác, trích xuất bí mật hoặc payload.

## 7. Tiêu chí khi kiểm chứng một môi trường local

1. Giữ binary, dữ liệu, cấu hình và fixture xác định; ghi phiên bản công cụ thực tế.
2. Phân biệt đóng gói/chạy binary gốc với tự viết lại server. Chưa có source nên không gọi bản tự dựng là tương đương nếu chưa có kiểm thử đối chiếu.
3. Ghi kết quả khởi động và tải dữ liệu riêng với kết quả kiểm tra thuật toán. Server khởi động thành công không phải solve thành công.
4. Dùng bảng logits ở trên làm dữ liệu đối chiếu cho lớp classifier. Kiểm tra đọc int8, thứ tự chiều, bias và margin.
5. Chỉ gọi pipeline vision tái lập thành công khi so sánh được đầu ra từng bước với dữ liệu tham chiếu; không suy ra từ tên model giống nhau.
6. Chỉ đánh dấu hoàn thành challenge khi có verifier độc lập kiểm tra đủ điều kiện gốc và bằng chứng acceptance phù hợp. Đọc fixture từ môi trường, tệp hoặc bộ nhớ không đáp ứng tiêu chí này.

Chưa khởi chạy hoặc thay đổi server trong lần tổng hợp này. `script/worker-report.json` vẫn là `not_verified` / `unsolved`.

Bổ sung: xem `CRYPTO_WORKFLOW_RESULT.md` và `offline_cache_verify.py` cho mô hình toán tường minh và lệnh tái lập kiểm chứng cache. Đây là kết quả của một lớp, không phải solver hoàn chỉnh.
