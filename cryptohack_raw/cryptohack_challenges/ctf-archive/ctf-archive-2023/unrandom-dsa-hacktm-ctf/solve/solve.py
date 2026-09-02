#!/usr/bin/env python3
import os
import re
import sys
import math
import socket
import hashlib
import subprocess
from pathlib import Path

HOST = "archive.cryptohack.org"
PORT = 2783
SERVER = "/mnt/data/unrandom_work/unrandom-dsa-hacktm-ctf/files/server_e1fddd4e52f996c291ef673085e2aa43.py"
MSG = b"sign me!"

q = 1092879518352786989476299662120803780680413706031
p = 114980098122485644081909328545152318405028145088847882027317345013981388286575240347125988913962377008079185186933737150634737906373997998255973998618830696124641699989832040024534816182819695513960388722708612198637142461508712377479624164082660449737112513197842864862118117988556791583132103431590243905887
g = 71362406463581247945079271940098275612978098529112230600196796189140192950767232739743735341187661340987005360553487990166878609700525413571064214225324658012470700433870690824682539895944119409587037738174278858905927291529426975193769936124742899736612599175814279682889152126395064937154831477977973692895
d = 653707

# This seed makes PyCryptodome's Miller-Rabin bases deterministic:
# - for p: base 2, harmless because p is prime
# - for q: a constructed strong liar base, repeated for all 30 rounds
seed_hex = """299d4d462370567a6217b811732b076d061aea5d62a2624678d5ba913a676e5f30ac7daba504c8e279f2400a7bbdef0f56359365282ace53f693a8f33b5c1d8897f3e9600f2779233cc8d1fc22b34b76e0aff32d9f42ac7ae85f664fc63c61e3183494d58c784e7dbc8a1e3b5133d92ffd6933580c2e9c7b1d8e9886d535ccc47fa926676ff3fbdb61dc8af4c60b159cecb3360413033f64e0087d3ea0d3db6cbad1597494e8651b9c824b9dfffa38eb4af51cf5662dec81aeb3068e6ac0e56e732e7b6acbe1f0134f050b8cf5cfd067de7253b79a518fb5844e0ec79152edcd135771b4247e87101e42082fb231c0079dc5e58c9cb5f49126b2c237488c2125756d6073cca48985bec2df2921cb2a6c7b9c60ef5dcd3c56c87f361aeb879c3ac0e32d89c9ed9f3876ffc3da8a4ef2ea209d994cb38b9d46b1c944d1fb4cf4ce67ff6399873a5df9156803f6f64b7c5b974a1ac43ab8528c7d1ce620e0097b99b39e2df73702a23629928e424247173ebff45c1db85ec62c5cc42d3a29357640e91248a1d7ed1826ed0bafbe3c9231953ac25c3bf5c4a804b5fe951839129749ebee636c03306c3488ea4133b5347c36b739727f0536e3a427800cb19f8dd3e49d5a063506961a9b19e338f864408e756d1555fa87c7b3c313fb406c8019e7ebaaa3fa85a25ad675ed73a75c33550376a8a6d762c65af307c675577093c021641744dc28d4176367c7147f4fa57f79cb167d566b8c1ca9f0978b54a301730bb88aa0b65891b310a3eb834016ddffb5370451c70efdbbfd0ed93556ca8ec39ca29144586fd0c2da86fb45dd42020fdb4d9754809fc77aa222be1a7bb2a4b6e1447455a61f41fc962630d896e055d7077e6b88f341f4b8e622d95a02d908ee4f960798e393067c604b9069e768b6fa6ef16ce03e5be016a05252964139ae973f2667580c52d74105fcb502c3365d90a03638b42b2228ded63918274f37056dd0a54f53195a3d8cd40fb74518b9179754d361ba13da515189364a9eb4e800f65bde95e3228f6e1b20cb694cdf4ab300193f6904bd0528f2fa682113fb52ca11722f4ac7a7bc05f2311f2d2ecec083389af04514210e59314ef5befdd7632ccc0dd69c8c62b2ef16db3e694271bcf386d1eef528bdc02b30ccfed81095452b53c62756137a000311545cac8aa4c9e45a4f5d9f55ed121c2f4fa9d97f20c18eedeb4c0830c8be1357827663fde770a3b3a106970fe4b2fee3d7b315ea9d11e2c035bedb0302a0c8470769d22a9d7c2e11bfdfb36bf4e1786acb9a1d8780dd003cf3317deeb1a717bf2f39540d1931003958693ea2b3420eb11a6407969647a0512f710f4cbb6e80f7487a22eff221a8d92cafbc25984e07077320aa0a29a5ed86d976dffffde8f1329395ec395f73b12a53d1dee3325d630806a67a91fd884dd08aa9f4d7b3f9de82357819fd5387e2f3e2247945efb87302f8af8dcb194c26ecc68c2f0cfc85bb567e25357916f471c42aa90570a0a299412ee2e0eeee4a90959388c1aeb7f612ce5724f6a77f4ca4bb654698a7f05523873fe70b9537529147ff18d476f34e87121e22537358500acf037c276b4d39e58e5a1c017c572f1ed4d5d74d2c3ccda2006b55e31246bb4770906e5ab3f3ea3f2187a429c3438fc27ae570bf39fb576ad70448a5519e51bbc81a878429790eb8500ab63cf07b0913dca24d291d7dfa63662e415859eb013103f5d1bd5072940b917792539f4ccd2ea0f7cada5a9cfed6e566334f356faeb592f18e85c2c509d7f016282f023bd3d56fa0f582cc20bf3b39208a33fb5e51dfdcf56811b4f90e357d4f36c4f3af8310c64a9a9a3dce190b113d2dc987989621465e022070e33e98f1241373bd4094e0af4f7f14d35f29ca3f1e009932a1de30d2e18cee1e83d43a043b3d3b2006d429c2b0c4a6c2200770312a3bbc1b21a3abedcb9ab7b0dbc6b65a0783c19c9b08c7bb6d80b493ac83a66e72a95f1c7d44ce79a226cf231fe1063b4b4802cb3f869f9ba96b04ce4f0decc0c32d3e7efc7ea6f2e494d4f9fa3687c7ebe5ec87a66398f3284bf507c20f770936ac14146d586dcb84e234176978be00593e140188da8139b5953de831779ee5fe990a7e69f4165863284b4cabadd4dcf3f9681ab32f4a935ecce92a609ccebb69b1f3cb22ef589d379721d211d678ed2cbbd4ee6767d71e2ea9a300ae30219114f39d0333d7ccbe511d2c5097b8b2256917b457d1d0f70133924c908f4a6f2600865bebf129058305c515f791df8c1d2e5e6def2d3d15bff3867a8364961ca251db29f3a9bd0aeeb7cb068cb36843832eb4c13b8dbea6fac6ca248bd85a07be4f79d093eb4a4f414e6c699cf37c6e668b5c3b550097087320bd016c07937f67689b83cbd01d34f278770308753c15c8c3d2c57e92ecf86cd5ce4b9dc02ce6251ce3acd243eaee7b73bfa360443f906e7ed0e75a439fd8d5412bf749de8713c13979586620bb71d323463c3e8984396f4cfc2cd040a42c71e2bc9ea47efb7c0393a90d131e71049792482951ad1d232aa86288a4c7aff77e423dc52b7bae228ba4005295e79852d36fd730d6932a844de1ae1a5f2abde1e9b6c67eeb9924ea53ebbc91ab0590b94602f8fc2183f99ffb806ff9ed6af843642010821e296b3d2197968cefd11ce8ab2775ebb49e75f27962ca6a48c7df6dbe54e0482eb812a462634fbf305348329845f3ac3b119a6d95f5b188cbb435d5fbd7b2ea9f94e96898d3c287445ca7a31aed6eb67ee72329c2d985d146f375d1b71b29b53f6444096cd9998caa54d1ac41c769dd9215542e3d875c1ea6b562f0ee1e0920d494617b00f34af8e728edb62ae100f21c411180992d2d17817304a4bf0552ee236fe762312785cc01ccab962946b0e9ceb76be846c1e6bd9e38843e6b75c728d030ea668bee99da667789bd54daf0268a5a1fc5d57d87ff2bc15c2dd9e15e34662890e8b6885d3c432350a5bfa48cb587c5b40d766b8b9f9133a25e65c947231a9a6ad8c804b9af445eae5ee5cd8c07a7fbf6969991cd92af3dbf48f152e9d36407aece15ab2e65d0b47296ab822af35418f0a6f08469936eb6e3b8a8bb82e07006d39dbaaa648eda2bdbe192a6de40b972f985f573b81ceb013b66819c669a8718fd0d6310df320147bf4b2acd96244e707ee85ebda2ec6abfa3f9a2be32287546b501aea213262420ad24036b6e6ed3638593af7823deca91da122d3b94b532eee516c1d023f7eb6ce95122375bc6a80e6a50517d1a03d6072b360305415eb0249013ce0f93893df0b11d48f9213303cbdf2976c203e9ea65f4da2b18dcf389ea6108738b04afb0272eed40ea5df9eeb0e8fd86ac0b95a232fa2ee62db8a2f10d25ff6b45f8c8c886add2ba4f59fc9499976dbc9dd09a88035c01ec75448cf15ef52f896fc9e64478a0392bcfed9d19129f2dab1b993616fa7206711a3848b5da177d425acf275d30b9c96c0a6dbd8d550b12422b30d8e7d6bb0076f64f""".replace("\n", "")

class Tube:
    def recvuntil(self, marker: bytes) -> bytes: raise NotImplementedError
    def sendline(self, data: bytes) -> None: raise NotImplementedError
    def recvall(self) -> bytes: raise NotImplementedError

class ProcessTube(Tube):
    def __init__(self, argv):
        env = os.environ.copy()
        env["FLAG"] = "FAKEFLAG{LOCAL_SOLVER_WORKS}"
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    def recvuntil(self, marker):
        data = b""
        while marker not in data:
            ch = self.p.stdout.read(1)
            if not ch: break
            data += ch
        return data
    def sendline(self, data):
        self.p.stdin.write(data + b"\n")
        self.p.stdin.flush()
    def recvall(self):
        return self.p.communicate(timeout=20)[0]

class SocketTube(Tube):
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=20)
        self.s.settimeout(20)
    def recvuntil(self, marker):
        data = b""
        while marker not in data:
            data += self.s.recv(1)
        return data
    def sendline(self, data):
        self.s.sendall(data + b"\n")
    def recvall(self):
        chunks = []
        try:
            while True:
                chunk = self.s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except socket.timeout:
            pass
        return b"".join(chunks)

def bsgs(base, target, mod, order):
    m = math.isqrt(order) + 1
    table = {}
    e = 1
    for j in range(m):
        table.setdefault(e, j)
        e = (e * base) % mod
    factor = pow(pow(base, m, mod), -1, mod)
    cur = target
    for i in range(m + 1):
        if cur in table:
            ans = i * m + table[cur]
            if ans < order:
                return ans
        cur = (cur * factor) % mod
    raise RuntimeError("discrete log failed")

def forge(y):
    x_mod_d = bsgs(g, y, p, d)
    z = int.from_bytes(hashlib.sha256(MSG).digest()[:20], "big")
    rr = g % q
    ss = (z + rr * x_mod_d) % d
    if ss == 0:
        ss = d
    while math.gcd(ss, q) != 1:
        ss += d
    return rr.to_bytes(20, "big") + ss.to_bytes(20, "big")

def solve(tube):
    tube.recvuntil(b"q = ")
    tube.sendline(str(q).encode())
    tube.recvuntil(b"p = ")
    tube.sendline(str(p).encode())
    tube.recvuntil(b"g = ")
    tube.sendline(str(g).encode())
    tube.recvuntil(b"What's your favorite number (hex): ")
    tube.sendline(seed_hex.encode())
    line = tube.recvuntil(b"sign = ")
    m = re.search(rb"y = (\d+)", line)
    if not m:
        raise RuntimeError("could not parse y from: " + repr(line))
    y = int(m.group(1))
    sig = forge(y)
    tube.sendline(sig.hex().encode())
    return tube.recvall()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    if mode == "remote":
        tube = SocketTube(HOST, PORT)
    else:
        tube = ProcessTube([sys.executable, SERVER])
    print(solve(tube).decode(errors="replace"))
