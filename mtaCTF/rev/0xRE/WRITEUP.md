# 0xRE - Writeup (mtaCTF)

- **Challenge:** `0xRE`
- **Category:** `Reverse Engineering / Kernel Rootkit & Forensics`
- **Points:** 500
- **Description:** `Rootkit is simple, right?`
- **Given Files:** `chall.zip` containing `Wincollect.sys` (27.7 KB) and `Triage.vhdx` (1.7 GB)
- **Flag:** `MTA60{R00tkit_Is_s1mple!R1ght?}`

---

## 1. Tổng quan kiến trúc & Chuỗi khai thác (Overview & Architecture)

Thử thách yêu cầu phân tích một chuỗi mã độc Windows Kernel Rootkit đa tầng kết hợp kỹ thuật điều tra số trên ảnh ổ đĩa Triage:

```
[Wincollect.sys] (Driver x64 ban đầu)
       │  (Đọc Registry Parameters0, giải mã RSA-4096 + Rolling XOR)
       ▼
[embedded.sys] (Rootkit Minifilter Driver ẩn náu trong kernel)
       │  (Đọc Registry Parameters1 & Parameters4, giải mã RSA-4096 thứ 2)
       ▼
[svchost.exe Injection (QueueUserAPC)]
       │  (Injected DLL 1: CLR Host nạp môi trường .NET Runtime)
       ▼
[injected_dll2.dll (.NET RAT Client)]
       │  (Giải mã 2 tầng Shellcode tài nguyên Oncode)
       ▼
[final_Oncode.dll (C2 Client & Persistence)]
       │  (Tính MD5("ADMIN") -> Tra cứu Registry Cell bị xóa/ẩn trong Triage)
       ▼
[Registry Cell: 73@AC@D9...E3ht]
       │  (Giải nén .NET GZip stream)
       ▼
Flag: MTA60{R00tkit_Is_s1mple!R1ght?}
```

---

## 2. Phân tích chi tiết từng tầng (Detailed Analysis)

### Giai đoạn 1: Phân tích `Wincollect.sys` (Stage 1 Loader Driver)

1. **Khởi tạo và đọc cấu hình Registry:**
   - Hàm `DriverEntry` / `sub_1400013D0` mở khóa Registry của dịch vụ tại đường dẫn `%wZ\Parameters` (tương ứng `ControlSet001\Services\winscollect\Parameters`).
   - Đọc tham số nhị phân `Parameters0` (kích thước `47,032` bytes).

2. **Thuật toán giải mã RSA-4096 & Rolling XOR:**
   - 512 bytes đầu tiên của `Parameters0` là ciphertext mã hóa RSA.
   - Section `.data` của `Wincollect.sys` tại `0x140005000` lưu trữ trực tiếp Public Modulus $N_0$ (RSA-4096, 512 bytes) với Public Exponent $e = 65537$.
   - Tính toán giải mã:
     $$m = c^e \pmod{N_0}$$
   - Loại bỏ padding PKCS#1 v1.5 (`00 01 FF ... FF 00`), trích xuất được:
     - Độ dài payload: `46,520` bytes (`0x0000B5B8`).
     - Khóa MD5 / XOR key: `93f23fb8727585cba419ea4ffdda6578` (16 bytes).
   - Phần payload còn lại (bắt đầu từ offset 512) được giải mã theo thuật toán Rolling XOR:
     $$\text{dec}[i] = \text{enc}[i] \oplus \text{key}[i \pmod{16}] \oplus \left(i + \left\lfloor\frac{i}{255}\right\rfloor\right) \pmod{256}$$
   - MD5 của payload sau giải mã khớp chính xác 100% với khóa trích xuất.

3. **Trích xuất `embedded.sys`:**
   - Payload giải mã chứa cấu trúc header gồm 4 DWORDs `[0x0, 0x9b0, 0xabf8, 0xb5a8]`.
   - Tại offset `0x9b0` (kích thước `44,024` bytes) là file PE Windows Kernel Driver thứ hai: **`embedded.sys`**.

---

### Giai đoạn 2: Phân tích `embedded.sys` (Stage 2 Kernel Rootkit)

1. **Chức năng Rootkit nhân:**
   - **Minifilter File Hooking (`FLTMGR.SYS`):** Đăng ký filter ẩn và chặn truy cập vào các thư mục nhạy cảm (lấy từ `Parameters4`: `\??\C:\ProgramData\OneDrives6` và `\??\C:\ProgramData\OneDrive`).
   - **Registry Filtering (`CmRegisterCallbackEx`):** Ẩn các key và value cấu hình mã độc.
   - **Process Protection (`ObRegisterCallbacks`):** Chặn các công cụ phân tích mở handle tiến trình.
   - **Network Sniffing/Filter:** Gắn vào thiết bị mạng `\Device\Nsi`.

2. **Giải mã tham số giai đoạn 2:**
   - `embedded.sys` chứa một khóa RSA-4096 thứ hai trong `.data` tại `0x14000A000`.
   - Giải mã `Parameters1` (`435,456` bytes) thu được payload tiêm tiến trình (434,944 bytes, MD5 `b4af17a24573dcf4d8394f533ea888b9`).
   - Driver tìm kiếm tiến trình `svchost.exe` (Session 0, quyền `SYSTEM`) và sử dụng cơ chế Asynchronous Procedure Call (**QueueUserAPC**) để tiêm payload này vào user-mode.

---

### Giai đoạn 3: Phân tích Payload tiêm tiến trình (.NET C2 RAT)

1. **CLR Hosting & Trích xuất Assembly:**
   - Payload tiêm gồm `injected_dll1.dll` (DLL C++ Native thực hiện gọi COM `mscoree.dll!CLRCreateInstance` để khởi động .NET CLR trong `svchost.exe`).
   - Section `.data` của DLL chứa 2 tệp Assembly .NET:
     - `injected_dll2.dll` (`newClient` - RAT Client).
     - `injected_dll3.dll` (`Interop.TaskScheduler` - Dùng tạo persistence Task `"Interop OneDrive Standalone"`).

2. **Giải mã 2 tầng Shellcode:**
   - Trong tài nguyên của `injected_dll2.dll`:
     - Tài nguyên `session` (33,472 bytes) $\to$ giải mã 2 lớp shellcode (marker `aaaa`, $k_1 = \text{0x6A28}, k_2 = \text{0x247B}$) ra `final_session.dll` (Keylogger & Chụp ảnh màn hình).
     - Tài nguyên `Oncode` (164,032 bytes) $\to$ giải mã 2 lớp shellcode (marker `aaaa`, $k_1 = \text{0x0B70}, k_2 = \text{0x14C5}$) ra `final_Oncode.dll` (C2 RAT Client chính).

---

### Giai đoạn 4: Phân tích C2 Configuration & Trích xuất Flag từ Triage

1. **Cơ chế lưu trữ cấu hình C2:**
   - Trong mã nguồn dịch ngược `newClient.Utilities.Inject`:
     ```csharp
     string hash = Hash.GetHash(Environment.MachineName, "@");
     using (RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + hash))
     {
         registryKey.SetValue(hash + "ht", GZip.Compress(Encoding.UTF8.GetBytes(config.host)));
     }
     ```
   - Trong ảnh ổ đĩa `Triage.vhdx` (hive `SYSTEM`), tên máy nạn nhân là `ADMIN`.
   - Tính toán giá trị băm:
     $$\text{MD5}(\text{"ADMIN"}) = \text{73ACD9A5972130B75066C82595A1FAE3}$$
     $$\longrightarrow \text{Key} = \text{SOFTWARE\73@AC@D9@A5@97@21@30@B7@50@66@C8@25@95@A1@FA@E3}$$
     $$\longrightarrow \text{Value} = \text{73@AC@D9@A5@97@21@30@B7@50@66@C8@25@95@A1@FA@E3ht}$$

2. **Trích xuất Registry Cell & Giải nén:**
   - Quét cấu trúc Registry Cell trên ảnh đĩa thu được cell nhị phân tại offset `0x76021600` / `0x76056600`:
     - Kiểu dữ liệu: `REG_BINARY` (3)
     - Dữ liệu: `1F 8B 08 00 92 95 38 6A 00 FF ...` (.NET GZip stream)
   - Sử dụng `zlib`/`gzip` giải nén stream này thu được chuỗi bí mật:
     ```text
     R00tkit_Is_s1mple!R1ght?
     ```
   - Chuẩn hóa theo format flag của giải đấu `MTA60{...}`:
     ```text
     MTA60{R00tkit_Is_s1mple!R1ght?}
     ```

---

## 3. Mã khai thác tự động (Full Python Solver)

Lưu tại [solve.py](file:///home/light/Workspace/CTF/mtaCTF/rev/0xRE/solve.py):

```python
import struct
import hashlib
import zlib
import pefile
from Registry import Registry

print("=" * 60)
print("[*] STEP 1: Trích xuất khóa RSA từ Wincollect.sys và giải mã Parameters0")
print("=" * 60)

pe_wincollect = pefile.PE("Wincollect.sys")
data_sec0 = [s for s in pe_wincollect.sections if b".data" in s.Name][0]
raw_data0 = data_sec0.get_data()
N0 = int.from_bytes(raw_data0[0:512], "big")
e = 65537

reg_system = Registry.Registry("SYSTEM")
params_key = reg_system.root().find_key("ControlSet001\\Services\\winscollect\\Parameters")
p0 = params_key.value("Parameters0").raw_data()

c0 = int.from_bytes(p0[:512], "big")
m0 = pow(c0, e, N0).to_bytes(512, "big")
sep0 = m0.find(b"\x00", 2)
v7_0 = m0[sep0 + 1:]
len0 = struct.unpack("<I", v7_0[:4])[0]
md5_0 = v7_0[4:20]

enc_payload0 = p0[512:512+len0]
dec_payload0 = bytearray(len0)
for i in range(len0):
    dec_payload0[i] = enc_payload0[i] ^ md5_0[i & 0xf] ^ ((i + i // 0xff) & 0xff)

assert hashlib.md5(dec_payload0).digest() == md5_0
print(f"[+] Parameters0 đã giải mã thành công ({len(dec_payload0)} bytes), MD5: {md5_0.hex()}")

embedded_pe_data = dec_payload0[16+0x9b0 : 16+0x9b0+0xabf8]
print(f"[+] Trích xuất embedded.sys ({len(embedded_pe_data)} bytes)")

print("\n" + "=" * 60)
print("[*] STEP 2: Trích xuất khóa RSA từ embedded.sys và giải mã Parameters1")
print("=" * 60)

pe_embedded = pefile.PE(data=embedded_pe_data)
data_sec1 = [s for s in pe_embedded.sections if b".data" in s.Name][0]
raw_data1 = data_sec1.get_data()
N1 = int.from_bytes(raw_data1[0:512], "big")

p1 = params_key.value("Parameters1").raw_data()
c1 = int.from_bytes(p1[:512], "big")
m1 = pow(c1, e, N1).to_bytes(512, "big")
sep1 = m1.find(b"\x00", 2)
v7_1 = m1[sep1 + 1:]
len1 = struct.unpack("<I", v7_1[:4])[0]
md5_1 = v7_1[4:20]

enc_payload1 = p1[512:512+len1]
dec_payload1 = bytearray(len1)
for i in range(len1):
    dec_payload1[i] = enc_payload1[i] ^ md5_1[i & 0xf] ^ ((i + i // 0xff) & 0xff)

assert hashlib.md5(dec_payload1).digest() == md5_1
print(f"[+] Parameters1 đã giải mã thành công ({len(dec_payload1)} bytes), MD5: {md5_1.hex()}")

print("\n" + "=" * 60)
print("[*] STEP 3: Tính toán chuỗi băm Registry C2")
print("=" * 60)

machine_name = "ADMIN"
md5_machine = hashlib.md5(machine_name.encode("utf-8")).digest()
hash_val = "@".join(f"{b:02X}" for b in md5_machine)
val_name = hash_val + "ht"
print(f"[+] MachineName: {machine_name}")
print(f"[+] Registry Value Name: {val_name}")

print("\n" + "=" * 60)
print("[*] STEP 4: Quét Registry Cell trên Disk Image và giải nén Flag")
print("=" * 60)

with open("triage.raw", "rb") as f:
    raw_disk = f.read()

target_bytes = val_name.encode("ascii")
pos = raw_disk.find(target_bytes)
gzip_magic = b"\x1f\x8b\x08"
gpos = raw_disk.find(gzip_magic, pos)

dobj = zlib.decompressobj(31)
raw_secret = dobj.decompress(raw_disk[gpos : gpos + 1000]).decode("utf-8")

# Chuẩn hóa format MTA60{...}
flag = f"MTA60{{{raw_secret.split('{')[-1].rstrip('}')}}}" if "{" in raw_secret else f"MTA60{{{raw_secret}}}"

print(f"\n[>>>] FLAG: {flag}\n")
```

---

## 4. Flag

```
MTA60{R00tkit_Is_s1mple!R1ght?}
```
