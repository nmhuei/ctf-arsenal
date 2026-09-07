# Writeup: The pyjail (TFC CTF 2026)

| Property | Value |
| :--- | :--- |
| **Category** | `Misc / PyJail` |
| **Points** | `214` |
| **Author** | `Hiumee` |
| **Solves** | `68` |
| **Python Version** | `CPython 3.15.0rc2` |

---

## 📝 Tổng Quan Bài Toán (Challenge Overview)

Server cung cấp một TCP socket (port 1234) chạy service Python 3.15 RC. Khi kết nối, người dùng gửi code và code được ghi vào file `user_input`. Sau đó, tiến trình tạo luồng chạy `os.system("python3 user.py")`.

Mã nguồn `user.py`:
```python
import sys
def idk(a, b, fn):
    fn(a, b)
code = ''.join(c for c in open("user_input").read() if c in "abcdefghijklmnopqrstuvwxyz:_.[],")
if "ass" in code or "typ" in code or "als" in code:
    print("Nope")
else:
    eval(code, {"__builtins__": {"idk":idk,"sys":sys}})
```

### Các ràng buộc (Constraints):
1. **Whitelist ký tự**: Chỉ cho phép chữ thường `a-z`, dấu hai chấm `:`, dấu gạch dưới `_`, dấu chấm `.`, dấu ngoặc vuông `[]`, dấu phẩy `,`.
2. **Không có dấu cách / newline**: Toàn bộ whitespace bị loại bỏ sạch.
3. **Không có dấu ngoặc tròn `()`**: Không thể gọi hàm trực tiếp `func()`.
4. **Không có dấu nháy / số**: Không có `'`, `"`, `0-9`.
5. **Blacklist từ khóa**: Cấm `"ass"` (chặn `__class__`), `"typ"` (chặn `type`), `"als"` (chặn `globals`, `locals`, `False`).
6. **Builtins bị tước bỏ**: Chỉ có `idk` và `sys`.

---

## 🔍 Phân Tích Kỹ Thuật & Lỗ Hổng (Root Cause & Primitives)

### 1. Primitive 1: Kích hoạt `fn(a, b)` không cần dấu ngoặc `()`
Hàm `def idk(a, b, fn): fn(a, b)` chấp nhận 3 tham số.
- Khi gán `idk.__defaults__ = (a, b, fn)`, ta có thể gọi `idk()` với 0 tham số và nó sẽ tự động chạy `fn(a, b)`.
- Python runtime tự động gọi `sys.stdout.flush()` với 0 tham số khi kết thúc tiến trình.
- Do đó:
  ```python
  sys.stdout.flush = idk
  ```
  khi `user.py` kết thúc, CPython runtime sẽ tự động gọi `idk()` $\implies$ kích hoạt `fn(a, b)`.

### 2. Primitive 2: Tính năng mới của Python 3.15 — `sys.remote_exec(pid, script)`
Python 3.15 bổ sung hàm nội tại `sys.remote_exec(pid, script)` cho phép một tiến trình Python inject và thực thi mã trong luồng chính của một tiến trình Python khác (cùng UID).
- Trong Docker container, tiến trình cha server (`jail.py`) là **PID 1**.
- Tiến trình con `user.py` chạy `sys.remote_exec(1, "user.py")` sẽ ép PID 1 chạy mã của `user.py` với toàn bộ biến global của server (`client_socket`, `time`, `f`).

### 3. Primitive 3: Phân biệt tiến trình con và PID 1 (Condition Branching)
Trong tiến trình con: `sys.argv[0]` là `"user.py"` (bắt đầu bằng ký tự `'u'`).
Trong PID 1: `sys.argv[0]` là `"/app/jail.py"` (bắt đầu bằng `'/'`).
Đường dẫn `sys.executable` là `"/usr/local/bin/python3"` (bắt đầu bằng `'/'`).
- Biểu thức phân nhánh boolean không cần từ khóa bị cấm:
  ```python
  cond = "[[sys.argv[sys.f][sys.f]]in[[sys.executable[sys.f]]]][sys.f]"
  ```
  - Trong con: `'u' in '/'` $\rightarrow$ `False` (`0`).
  - Trong PID 1: `'/' in '/'` $\rightarrow$ `True` (`1`).

### 4. Primitive 4: Khử lỗi khoảng trắng bằng Target Unpacking
Khi không có dấu cách, mọi cấu trúc dạng `for m in sys.modules` sẽ biến thành `forminsys.modules` gây `SyntaxError`.
Giải pháp: Sử dụng unpacking target list với dấu ngoặc vuông phân cách token tuyệt đối:
```python
[[sys]for[x,x,...,sys.m,...]in[[],[[sys.modules]][sys.f]][cond]]
```
Trong PID 1, `sys.modules` có 51 keys và key thứ 19 luôn là `'__main__'`. Thao tác này trích xuất trực tiếp `sys.m = '__main__'`.

### 5. Primitive 5: Hook vĩnh viễn vòng lặp server (`time.sleep`)
Trong PID 1:
```python
sys.u = sys.modules[sys.m].f.name  # "user_input"
idk.__defaults__ = (sys.u, sys.remote_exec)
sys.modules[sys.m].time.sleep = idk
```
Server `jail.py` luôn chạy `time.sleep(1)` sau mỗi request. Bằng cách thay thế `time.sleep = idk`, bất kỳ kết nối tiếp theo nào gửi mã vào `user_input` đều được PID 1 thực thi trực tiếp qua `sys.remote_exec(1, "user_input")`!

### 6. Primitive 6: Unicode Normalization Bypass (NFKC)
Ở lượt kết nối thứ hai (hoặc mọi lượt gửi payload về sau), ta gửi code Python thuần túy nhưng biến đổi các định danh thành ký tự Unicode Mathematical Bold (ví dụ `𝐞𝐱𝐞𝐜`, `𝐜𝐡𝐫`):
- Khi `user.py` đọc `user_input`, bộ lọc `if c in "abcdefghijklmnopqrstuvwxyz:_.[],"` loại bỏ toàn bộ ký tự Unicode $\implies$ chuỗi rỗng $\implies$ tiến trình con không can thiệp.
- Khi PID 1 đọc `user_input` qua `sys.remote_exec`, trình phân tích CPython tự động chuẩn hóa NFKC chuyển `𝐞𝐱𝐞𝐜` thành `exec`, thực thi payload tùy ý với quyền root!

---

## 💻 Khai Thác & Môi Trường Local Lab

### 1. Khởi động Lab Local
```bash
./script/run_lab.sh 1337
```
Container `pyjail-lab` sẽ lắng nghe tại `127.0.0.1:1337`.

### 2. Sử dụng Interactive Shell
Tool tương tác đã được xây dựng tại [`script/shell.py`](../script/shell.py):
```bash
python3 script/shell.py --port 1337
```
Giao diện shell cho phép gõ bất kỳ lệnh Linux nào (đáp ứng < 0.3s):
```text
pyjail-lab# id
uid=0(root) gid=0(root) groups=0(root)

pyjail-lab# cat /flag.txt
TEST{flag}

pyjail-lab# uname -a
Linux 356482795d4e 7.0.12+kali-amd64 ... x86_64 GNU/Linux
```

Hoặc chạy lệnh đơn:
```bash
python3 script/shell.py -p 1337 -c "cat /flag.txt"
```

### 3. Chạy Exploit Solve
```bash
python3 solver/solve.py --host 127.0.0.1 -p 1337
```

---

## 🚩 Flag
- **Local Test Flag:** `TEST{flag}`
- **Challenge Status:** Solved (100% verified on local environment).
