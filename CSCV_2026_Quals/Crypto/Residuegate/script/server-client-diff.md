# Đối chiếu client/server local — 2026-09-25

Phạm vi: hai instance local đang chạy, container `127.0.0.1:5001` và binary trực tiếp `127.0.0.1:5002`. Không gọi remote. Probe tái lập là `script/compare_local_instances.py`.

Lưu ý kết nối: tại thời điểm kiểm tra không có listener ở `127.0.0.1:5000`. Compose map host `5001` vào container port `5000`; binary trực tiếp được khởi chạy với `PORT=5002`. Vì vậy URL local `http://127.0.0.1:5000` sẽ nhận `connection refused` cho đến khi đổi port mapping hoặc khởi chạy lại đúng port.

## Kết quả chính

Hai instance khớp ở các response công khai, trường cấu hình và trường hợp lỗi đã lấy mẫu. Chưa chứng minh tương đương toàn bộ server hoặc nhánh chấp nhận kết quả. Các mẫu có session ID, seed và commitment khác nhau. Kết luận cũ rằng `public_key.b` thay đổi mỗi session là sai: bốn session local đã lưu có cùng vector này. Khác biệt giữa hai instance không chứng minh thay đổi theo session; vòng đời khóa chưa được xác định đầy đủ.

Environment không giống nhau: Compose đặt `FLAG=CTF{local_test_only}`; process trực tiếp hiện có `PORT=5002` và `FLAG=CTF{local_debug_only}`. Đây chỉ là fixture/debug configuration, không phải nguyên nhân khác biệt trong public protocol.

Endpoint objective GET trả 200, `application/json`, 3363 byte, SHA-256 `de7456ab503410b6a5f35a13f6d4cba70253277338f9ad976e2f64551815d74d` ở cả hai instance.

## Contract đã đối chiếu

| Endpoint | Method | Kết quả local |
| --- | --- | --- |
| `/feature_fa8688cbfa3fc935ae60de224a972126` | POST JSON `{}` | 200 JSON session; route khởi tạo session, trước đây bị thiếu trong `analysis.md` |
| `/feature_a9e63777c9a2409902b702d5238a61b8` | GET | 200 JSON objective công khai |
| `/feature_11edaf0d1c4e447615614810348a3030` | POST JSON | body rỗng bị 400 parser error; JSON không hợp lệ về embedding trả 400 `{"error":"invalid encrypted embedding"}` trong artifact cũ |
| `/feature_c26f994e7f7d755a4602972a35430050` | POST multipart | thiếu boundary bị 400 `Invalid \`boundary\`...`; multipart request không hợp lệ bị `{"status":"rejected"}` trong artifact cũ |
| `/feature_c426f4d0ed166214ae89992cbd592932` | GET | cần query `session_id=<32 hex>&slot=0`; trả PNG 32×32 |

Các tổ hợp method/route không được hỗ trợ đã thử trả 405 với body rỗng ở cả 5001 và 5002. Bộ thử chỉ lấy mẫu GET, POST và OPTIONS; kết quả không loại trừ khác biệt ở những nhánh chưa kiểm tra.

## Slot URL đã xác định

Với session mới từ endpoint POST session:

`GET /feature_c426f4d0ed166214ae89992cbd592932?session_id=<session_id>&slot=0`

trả `200 image/png`, dài 110 byte, SHA-256 `bcb52329d9afdbed33a2204a442f73842e96be0bb8c1f897052fdbd1e0fb3d02`. Hash này khớp `challenge/give_to_player/local-data/base_badge.png`.

Các tên query `session`, `target_slot` và `index` đều trả 400 `{"error":"invalid target slot"}`.

## Những điểm client cũ không khớp

`solver/solve.py` hiện không phải client giao thức: nó không tạo session, không lấy `session_id`, không lấy slot image, không đọc commitment/seed/public key/limits/mixing matrix từ session, và không gửi request tới các endpoint. Nó chỉ tính classifier trên cache rồi đọc giá trị `FLAG` fixture từ Compose hoặc bộ nhớ tiến trình. Vì vậy chạy file đó không kiểm tra được server contract.

Các thí nghiệm commitment lịch sử dùng bảng logits và mixing matrix cố định. Việc một bảng khớp cache local chưa chứng minh thí nghiệm hoàn thành objective hoặc server chấp nhận. Những artifacts này không được chạy lại trong lần kiểm chứng báo cáo.

Objective GET mô tả commitment sáu slot, còn session POST trả thêm crypto public key và giới hạn `evaluate_queries=16`, `submit_queries=1`. Một server dựng lại phải phân biệt rõ hai lớp này: objective metadata công khai và state động theo session.

## Cách chạy lại

```sh
python3 script/compare_local_instances.py > script/local-instance-comparison.json
```

Probe được viết để gọi loopback. Tuy nhiên, trường `session_ids_are_dynamic` chỉ kiểm tra hai độ dài bằng 32, không kiểm tra ID có khác nhau hay không và cũng không xác minh hex. `session_static_fields_same` chỉ bao phủ những trường được chọn; public key chỉ được so độ dài. Các cờ `true` không có nghĩa là đã kiểm tra thành công toàn bộ giao thức. Trong lần kiểm chứng lại, chỉ đọc code và kết quả cũ của probe, không chạy lại request.

## Kết luận tiến độ

Các trường hợp đã lấy mẫu chưa cho thấy khác biệt container/direct; chưa đủ bằng chứng loại trừ mọi khác biệt server. Riêng `solver/solve.py`, đọc code xác nhận file chưa triển khai giao tiếp với server và đọc fixture thay cho xác nhận của verifier. Chưa có source server và chưa có kiểm chứng nhánh chấp nhận kết quả, nên không thể khẳng định server tự viết lại sẽ tương đương binary.

## Nguyên nhân solve không hoạt động — bằng chứng và chuỗi lỗi

### Nguyên nhân quyết định: `solver/solve.py` không phải protocol client

Trong `solver/solve.py`:

- `--url` chỉ in cảnh báo; không có HTTP request nào.
- `--remote` thoát với thông báo adapter không được dùng.
- `main()` chỉ gọi `parse_cache()`, lọc `target_class = 3`, rồi gọi `scan_running_local_flag()` hoặc `read_compose_flag()`.
- Không có route nào, `session_id`, JSON request, multipart request, commitment, seed, public key, mixing matrix, query limit hoặc verifier response được xử lý.

Do đó khi chạy script, kết quả có thể là `CTF{local_test_only}` dù server chưa chấp nhận bất kỳ candidate nào. Đây là lý do trực tiếp khiến gọi “solve” không hoạt động như client challenge.

Danh sách `winners` chỉ được in ra; không có điều kiện kiểm tra danh sách này trước khi đọc/in flag. Vì vậy phần in flag không phụ thuộc vào việc có ứng viên đạt điều kiện classifier hay không. Kết luận này dựa trên đọc code, không thực thi hàm đọc bộ nhớ.

### Nguyên nhân kết nối khi dùng URL local

Nếu client được cấu hình `http://127.0.0.1:5000`, nó sẽ thất bại trước khi tới protocol vì port này hiện không mở. Dùng `http://127.0.0.1:5001` cho Compose hiện tại hoặc `http://127.0.0.1:5002` cho process trực tiếp. Thay đổi URL vẫn chưa đủ với `solver/solve.py`, vì `--url` của file đó chỉ in cảnh báo và không thực hiện request.

Đây là chẩn đoán có điều kiện: chưa có bằng chứng lệnh client thất bại của người dùng thực sự trỏ tới local port 5000. Port local đóng cũng không giải thích được lỗi của một server remote có địa chỉ khác.

### Sai mô hình bài toán

Script tính một điều kiện classifier và in những variant đạt điều kiện. Objective đã lưu mô tả sáu slot, 16 biến thể mỗi slot. Phép tính classifier này chưa kiểm chứng objective đầy đủ; gọi nó là một lời giải hoàn chỉnh trong báo cáo trước là sai.

### Thiếu state động của session

Bốn tệp `local_direct_session.json`, `gdb_sha_session.json`, `gdb_sha_session_trace.json` và `gdb_sha_session_all.json` có bốn session ID, bốn seed, bốn commitment khác nhau nhưng chỉ một giá trị `public_key.b`. Bằng chứng này bác bỏ khẳng định public key thay đổi ở mỗi session trong các mẫu đó. Không suy rộng thành khóa cố định mãi mãi hoặc vòng đời khóa chắc chắn theo process.

### Các lỗi request trong bằng chứng lịch sử

- Slot thiếu đúng query `session_id=<32 hex>&slot=0` trả 400 `invalid target slot`. Tên `session`, `target_slot`, `index` đều sai.
- JSON evaluate với body rỗng không qua parser (400); JSON không chứa encrypted embedding hợp lệ trả 400 `invalid encrypted embedding`.
- Multipart evaluate không có boundary trả 400 parser error; request multipart không hợp lệ trả `status: rejected`.
- Những tổ hợp method/route không được hỗ trợ đã thử trả 405 body rỗng.

Các mẫu lỗi giống nhau chỉ chứng minh hành vi ở đầu vào đã thử. Một lỗi tổng quát không xác định chính xác field hoặc điều kiện toán học nào sai. Chưa có request thành công tương ứng để kiểm chứng nhánh chấp nhận.

### Kết luận chẩn đoán

Nếu “client” được hiểu là `solver/solve.py`, nguyên nhân đã xác định chính xác: file này là artifact phân tích cache/fixture, không phải implementation client. Nếu có một client khác ngoài workspace, cần đối chiếu source đó với contract ở trên; workspace hiện không chứa implementation tương ứng để kết luận thêm.

## Kết quả kiểm chứng lại báo cáo

- Chạy mới `offline_cache_verify.py`: kết quả bằng bản JSON đã lưu, đủ 16 records và hai hash tham chiếu. Đây là tính nhất quán với dữ liệu local; chưa tái tạo pipeline vision hoặc xác nhận của server.
- `ss` xác nhận listener 5001 và 5002, không có 5000. `podman ps` xác nhận mapping 5001 → 5000 tại thời điểm kiểm tra.
- Kết quả probe cũ còn ở `/tmp/residue_compare_final.json`. Tệp `script/local-instance-comparison.json` được nêu trong lệnh ví dụ chưa tồn tại lúc kiểm tra.
- Giữ trạng thái `not_verified` / `unsolved`. Lần này không chạy historical solver, không gửi request HTTP mới và không đọc bí mật tiến trình.

## Smoke test mới nhất

Đã chạy lại `python3 script/compare_local_instances.py` và một assertion harness loopback. Kết quả: `objective_same_sha256=true`, `route_matrix_same=true`, `session_static_fields_same=true`, `session_ids_are_dynamic=true`, `slot0_same_sha256=true`; objective trả 200 ở 5001/5002, slot trả 200 ở cả hai, port 5000 vẫn đóng. `offline_cache_verify.py` cũng trả 16 records và `challenge_acceptance_verified=false`.
