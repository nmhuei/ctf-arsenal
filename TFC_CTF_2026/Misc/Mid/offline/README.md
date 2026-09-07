# Bayes dừng sớm — mô phỏng offline

Script `bayes_search.py` chỉ mô phỏng toán học, không kết nối mạng.
Phụ thuộc: Python và NumPy.

Chạy từ thư mục challenge:

```bash
python offline/bayes_search.py --noise 0.1 --confidence 0.99
```

## Thuật toán

1. Khởi tạo xác suất đều cho các đáp án từ 0 đến `size - 1`.
2. Chọn ngưỡng q sao cho xác suất `secret <= q` gần 0,5 nhất.
3. Nhận câu trả lời Boolean, bị đảo độc lập với xác suất p đã biết.
4. Nhân xác suất mỗi ứng viên với `1-p` nếu phù hợp phản hồi, với p nếu không; chuẩn hóa tổng về 1.
5. Dừng khi xác suất lớn nhất đạt ngưỡng tin cậy hoặc hết ngân sách query.
6. Trả ứng viên có xác suất lớn nhất.

So sánh với cùng chính sách chọn query nhưng dùng đủ ngân sách. Hai phương pháp
dùng chung mật khẩu mô phỏng và các biến nhiễu theo bước để dễ tái lập.
Tie được giải bằng cách chọn chỉ số nhỏ nhất (NumPy argmin/argmax).

## Kết quả quan sát trước đó

10.000 lượt, 128 đáp án, tối đa 21 query, seed 20260908:

| Nhiễu | Thành công dùng đủ query | Thành công dừng ở 99% | Query trung bình dừng sớm |
|---|---:|---:|---:|
| 5% | 99,37% | 98,91% | 11,85 |
| 10% | 95,47% | 95,33% | 15,81 |
| 20% | 64,85% | 64,85% | 20,66 |

Lần đo trước dùng ngưỡng 100% làm baseline; ở nhiễu 5%, làm tròn số thực
khiến baseline đó dừng ở trung bình 20,99 query. Script đã lưu dùng `None`
để baseline luôn chạy đủ 21 query.

## Giới hạn

Đây là nhiễu độc lập với p đã biết, không phải cơ chế đổi trạng thái của challenge.
Không có phản hồi riêng cho trường hợp bằng nhau. Ngưỡng 99% là xác suất hậu nghiệm
trong mô hình, không phải bảo đảm đúng trong mọi tình huống. Số liệu là ước lượng
Monte Carlo; không nên coi chênh lệch nhỏ là có ý nghĩa thống kê khi chưa phân tích thêm.
Chi phí lưu phân bố tăng tuyến tính theo số ứng viên; cách liệt kê này chỉ dành
cho không gian mô phỏng nhỏ, không áp dụng trực tiếp cho không gian 62^30.
