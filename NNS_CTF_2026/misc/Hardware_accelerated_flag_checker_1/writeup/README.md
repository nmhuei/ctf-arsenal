# Writeup: Hardware accelerated flag checker 1

| Property | Value |
| :--- | :--- |
| **Category** | `misc` |
| **Points** | `69` |
| **Author** | `simen` |
| **Solves** | `160` |

---

## 📝 Challenge Overview

Tệp đính kèm cung cấp `netlist.v` — một mạch số Verilog đã tổng hợp (synthesized gate-level netlist) đóng vai trò kiểm tra flag.

## 🔍 Phân tích mạch số (Hardware Reversing)

1. **Cấu trúc Module**:
   - `input [6:0] character`: Ký tự ASCII 7-bit đưa vào ở mỗi chu kỳ xung nhịp.
   - `reg [4:0] s`: Trạng thái máy hữu hạn (FSM) gồm đúng 5 flip-flops (32 trạng thái: 0 đến 31).
   - `output found_flag`: Được kích hoạt khi `s == 5'b11111` (state 31).
   - `assign _000_ = ~(reset_n & _228_)`: Reset đồng bộ về 0 khi `reset_n = 0` hoặc khi đã tới state 31.
2. **Logic tổ hợp**:
   - 295 biểu thức `assign` chỉ chứa các cổng cơ bản NOT (`~`), AND (`&`), OR (`|`).
   - Các dây dẫn được sắp xếp theo thứ tự topo hoàn chỉnh (không có vòng lặp trễ).

## 💻 Phương pháp giải (BFS State Exploration)

Biên dịch 295 câu lệnh gán Verilog sang hàm chuyển trạng thái Python `step(s, char) -> (next_s, flag)`.

Chạy thuật toán BFS (Breadth-First Search) bắt đầu từ `s = 0` và duyệt qua các ký tự in được (ASCII 32–126). Chuỗi ký tự dẫn từ trạng thái 0 đến trạng thái 31 chính là Flag.

Mã nguồn giải hoàn chỉnh nằm tại [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `NNS{qu1ck_and_3ff1ci3n7_check5}`
