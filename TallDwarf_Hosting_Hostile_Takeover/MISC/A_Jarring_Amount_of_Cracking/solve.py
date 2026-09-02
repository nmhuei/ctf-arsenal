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
