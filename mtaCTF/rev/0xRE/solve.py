import struct
import hashlib
import zlib
import re
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

# Trích xuất embedded.sys từ payload0
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
print("[*] STEP 3: Trích xuất Assembly .NET và giải mã resource Oncode (2 lớp shellcode)")
print("=" * 60)

# Trong Parameters1: target process là svchost.exe, payload tại offset 144
# Injected DLL 1 chứa injected_dll2.dll tại offset 0x19360 trong Parameters1
pe2_data = dec_payload1[0x19360:]
pe2 = pefile.PE(data=pe2_data)
pe2_trimmed = pe2.trim()
print(f"[+] Trích xuất injected_dll2.dll (.NET RAT Client, {len(pe2_trimmed)} bytes)")

# Tìm chuỗi băm MachineName ADMIN
machine_name = "ADMIN"
md5_machine = hashlib.md5(machine_name.encode("utf-8")).digest()
hash_val = "@".join(f"{b:02X}" for b in md5_machine)
val_name = hash_val + "ht"
print(f"[+] MachineName: {machine_name}")
print(f"[+] Hash Key: {hash_val}")
print(f"[+] Registry Value cần tìm: {val_name}")

print("\n" + "=" * 60)
print("[*] STEP 4: Quét trực tiếp Registry Cell / Disk Image để lấy và giải nén Flag")
print("=" * 60)

with open("triage.raw", "rb") as f:
    raw_disk = f.read()

# Tìm vị trí cell registry chứa tên value val_name
target_bytes = val_name.encode("ascii")
pos = raw_disk.find(target_bytes)
print(f"[+] Tìm thấy Registry Key Cell tại offset: {hex(pos)}")

# Tìm stream gzip ngay sau cell
gzip_magic = b"\x1f\x8b\x08"
gpos = raw_disk.find(gzip_magic, pos)
print(f"[+] Tìm thấy GZip stream tại offset: {hex(gpos)}")

dobj = zlib.decompressobj(31)
flag = dobj.decompress(raw_disk[gpos : gpos + 1000]).decode("utf-8")

print("\n" + "=" * 60)
print(f"[>>>] FLAG THU ĐƯỢC: {flag}")
print("=" * 60)
