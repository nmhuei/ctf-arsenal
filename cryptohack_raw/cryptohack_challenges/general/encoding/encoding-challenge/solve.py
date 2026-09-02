import pwn
import json
import base64
import binascii
import codecs
from Crypto.Util.number import long_to_bytes

r = pwn.remote('socket.cryptohack.org', 13377)

def decode(t, d):
    if t == "base64":
        return base64.b64decode(d.encode()).decode()
    elif t == "hex":
        return binascii.unhexlify(d).decode()
    elif t == "rot13":
        return codecs.decode(d, 'rot_13')
    elif t == "bigint":
        return binascii.unhexlify(d[2:]).decode()
    elif t == "utf-8":
        return "".join([chr(b) for b in d])

while True:
    received = r.recvline().decode()
    if "crypto{" in received:
        print(received)
        break
    
    try:
        req = json.loads(received)
    except:
        print(received)
        continue
    
    if "type" in req:
        t = req["type"]
        d = req["encoded"]
        decoded = decode(t, d)
        
        r.sendline(json.dumps({"decoded": decoded}).encode())
