# Fruit Market — Writeup

## Tóm tắt

Challenge cho sẵn một mini market gồm 3 token APL, BAN, CHY và 3 pool:
- APL-BAN
- APL-CHY
- BAN-CHY

Mục tiêu là làm cho tài khoản `manager` có ít nhất 500 APL rồi gọi `/flag` để lấy cờ.

## Ý tưởng chính

Service phát event `new_trade` qua Socket.IO. Mỗi event chứa raw transaction `approve` và `swap` của bot trader. Ta không cần phá chữ ký hay sửa giao dịch của bot; chỉ cần:

1. nhận và relay lại approve/swap của bot đủ nhanh để market tiếp tục chạy,
2. cập nhật local model của reserves,
3. sau mỗi trade thành công, tìm vòng triangular arbitrage có lợi nhuận cao nhất:
   - `APL -> BAN -> CHY -> APL`
   - `APL -> CHY -> BAN -> APL`
4. thực hiện vài vòng arb, ưu tiên dừng sớm nếu queue còn event victim mới,
5. lặp lại cho đến khi APL >= 500.

## Phân tích mã solve

Solver khởi tạo 3 thứ quan trọng:
- account mới làm `manager`
- local reserves ban đầu cho 3 pool
- queue nhận các event `new_trade`

Các hàm đáng chú ý:

- `claim_basket()` nhận vốn khởi đầu 10 APL.
- `preapprove()` approve trước 6 cặp token/pool cần thiết.
- `decode_swap()` parse raw transaction của bot để biết pool, token vào, số lượng và deadline.
- `process_victim_batch()` relay batch victim trade, chỉ bỏ các trade đã hết hạn rõ ràng.
- `simulate_path()` và `best_apl_cycle()` mô phỏng 2 vòng triangular arb rồi chọn vòng lãi nhất.
- `drain_arbitrage()` thực hiện nhiều round arb, nhưng sẽ dừng sớm khi queue còn trade để tránh làm bot chết nhịp.
- `try_sync_reserves()` dùng `eth_call(getReserves)` để đồng bộ lại state khi có trade bị miss hoặc `swap not confirmed`.

## Tại sao hướng này hiệu quả

Bản chất đây là bài timing + arbitrage chứ không phải memory corruption hay signature forgery.

Điểm mạnh của solver cuối cùng:
- không can thiệp nội dung tx của bot,
- dùng `swap_hash` sẵn có để theo dõi victim swap,
- vẫn thử các trade có TTL sát 0/1 giây,
- resync reserves khi có lệch trạng thái,
- giảm số vòng arb khi queue còn bận, nên giữ market sống lâu hơn.

## Diễn biến exploit thực tế

Ban đầu account chỉ có 10 APL. Ngay trade đầu tiên, solver ăn được 2 vòng arb và nâng APL từ 10 lên 80.

Sau đó có vài lần `victim swap not confirmed`, solver đồng bộ lại reserves từ chain rồi tiếp tục chạy. Khi state market méo đủ mạnh, solver lấy được các round lời rất lớn, ví dụ có round tăng từ 80 lên 205.

Về cuối, khi APL đã cao, solver chuyển sang vét các vòng lợi nhuận nhỏ 1–2 APL để vượt ngưỡng 500. Ở lượt cuối cùng, APL tăng từ 494 lên 513, sau đó `/flag` trả về flag thật.

## Flag

`GPNCTF{lO0K_m4MA_I_Go7_5omE_frui7s_At_mY_JO8}`

## Chạy lại

```bash
python solve.py https://TARGET --max-trades 800
```

## Kết luận

Đây là một bài khai thác market state rất điển hình: relay flow của trader để giữ hệ thống sống, sau đó tận dụng price imbalance giữa 3 AMM pool bằng triangular arbitrage. Phần khó nhất không nằm ở công thức AMM mà nằm ở việc xử lý timing, backlog queue và resync trạng thái đủ ổn định để market không chết trước khi đạt 500 APL.
