# Writeup: A Jarring Amount of Cracking (TallDwarf Hosting Takeover)

- **Challenge**: A Jarring Amount of Cracking
- **Category**: MISC / Reversing
- **Points**: 292
- **Solves**: 9
- **Platform**: TallDwarf Hosting Hostile Takeover
- **Status**: SOLVED
- **Flag**: `TDHT{g8pV38UUuG2J4lMKqe30AzKQ}`
- **Solver**: `gpt` via Java Bytecode Obfuscation Analysis & AES Decryption

---

## 1. Challenge Overview
We are given a Minecraft PaperMC plugin: `MinecraftPlugin.jar`.
Disassembling with `javap` reveals control flow flattening and string obfuscation across `GenericMinecraftPlugin.class` and `a/a.class`.

---

## 2. Reverse Engineering Bytecode

1. In `dev.jimster.genericMinecraftPlugin.GenericMinecraftPlugin.onEnable()`:
   - Queries plugin metadata:
     - `name = getPluginMeta().getName()` (`GenericMinecraftPlugin` from `plugin.yml`)
     - `version = getPluginMeta().getVersion()` (`3.5.76-release` from `plugin.yml`)
   - Calls `a.a.a(name, version, 168443359)` to retrieve the secret flag.

2. In `a.a.a(String arg0, String arg1, int arg2)`:
   - Uses `invokedynamic` with `StringConcatFactory.makeConcatWithConstants` using template:
     `\u0001:\u0001:generic-main-r9837475:1776225256`
   - Formatted string:
     `GenericMinecraftPlugin:3.5.76-release:generic-main-r9837475:1776225256`
   - Computes `SHA-256` of this UTF-8 string to derive a 256-bit AES key.
   - IV (base64): `SKmLFkw/om7rawjVr4YsUg==`
   - Ciphertext (base64): `WWmdJ5BsZvzm00qrrbYumkfXK5mbpvgGrivHFuExja0=`
   - Mode: `AES/CBC/PKCS5Padding`

---

## 3. Solver Implementation (solve.py)

```python
import base64
import hashlib
from Crypto.Cipher import AES

def solve():
    name = "GenericMinecraftPlugin"
    version = "3.5.76-release"
    template = f"{name}:{version}:generic-main-r9837475:1776225256"

    key = hashlib.sha256(template.encode("utf-8")).digest()
    iv = base64.b64decode("SKmLFkw/om7rawjVr4YsUg==")
    ct = base64.b64decode("WWmdJ5BsZvzm00qrrbYumkfXK5mbpvgGrivHFuExja0=")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    flag = pt[:-pt[-1]].decode("utf-8")
    print("FLAG:", flag)
    return flag

if __name__ == "__main__":
    solve()
```

---

## 4. Output
```text
FLAG: TDHT{g8pV38UUuG2J4lMKqe30AzKQ}
```
