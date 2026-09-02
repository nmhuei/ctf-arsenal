import pwn
import json

r = pwn.remote('socket.cryptohack.org', 11112)
r.recvline()
r.recvline()
r.recvline()
r.recvline()
r.sendline(json.dumps({"buy": "flag"}).encode())
print(r.recvline().decode())
