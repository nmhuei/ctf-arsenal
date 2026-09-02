from pathlib import Path
import re

text = Path("output_c01a9cc6b744e13a3549f8c00ac7e095.txt").read_text()

vals = {
    k: int(v, 16)
    for k, v in re.findall(r"(p|y_A|y_B|c) = (0x[0-9a-f]+)", text)
}

p = vals["p"]
yA = vals["y_A"]
yB = vals["y_B"]
c = vals["c"]

sk = (yA * yB) ** 2 % p
m = c // sk

print(m.to_bytes((m.bit_length() + 7) // 8, "big").decode())
