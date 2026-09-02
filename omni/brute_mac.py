import subprocess
import re

def test_mac(mac):
    try:
        proc = subprocess.run(
            ["/home/light/GitHub/CTF/ctf_repo/IDA_pro/ida_keygen_v2", 
             "-u", "kali", "-e", "crack@done.com", "-t", "Computer", "-m", mac],
            capture_output=True, text=True, timeout=2
        )
        out = proc.stdout
        m = re.search(r"Generated license saved to: (idapro_.*\.hexlic)", out)
        if m:
            return m.group(1)
    except Exception as e:
        pass
    return None

# Let's try some MAC patterns
# Suffix we want: 575B-87D6-D6
# Let's try brute forcing the first byte if MAC is XX:57:5B:87:D6:D6
target = "idapro_48-575B-87D6-D6.hexlic"

print("Starting brute force...")
for x in range(256):
    mac = f"{x:02x}:57:5b:87:d6:d6"
    res = test_mac(mac)
    if res == target:
        print(f"[+] FOUND! MAC: {mac} -> {res}")
        break
    if x % 32 == 0:
        print(f"Tested up to {x}...")
else:
    print("Not found with XX:57:5B:87:D6:D6")
