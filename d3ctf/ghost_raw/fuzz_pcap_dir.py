import requests
import hashlib

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"
dir_url = f"{base}/test/7f9c18a2e44d/"

# Wordlist for filename generation
words = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100", "101", "102", "103",
    "flag", "flags", "secret", "secrets", "key", "keys", "admin", "root", "ops", "ops-root",
    "d3ctf", "ghost", "zero", "ghost_zero", "ghost-zero", "ghostzero",
    "log", "logs", "backup", "dump", "db", "database", "sqlite",
    "capture", "traffic", "pcap", "data", "test", "archive", "index",
    "primary", "legacy", "retired", "jwt", "rsa", "token", "auth",
]

candidates = set()
for w in words:
    candidates.add(w)
    candidates.add(f"{w}.pcap")
    candidates.add(f"{w}.txt")
    candidates.add(f"{w}.json")
    candidates.add(f"{w}.key")
    candidates.add(f"{w}.pem")
    h = hashlib.md5(w.encode()).hexdigest()
    candidates.add(h)
    candidates.add(f"{h}.pcap")
    candidates.add(f"{h}.txt")
    sha = hashlib.sha256(w.encode()).hexdigest()
    candidates.add(sha)
    candidates.add(f"{sha}.pcap")

print(f"Testing {len(candidates)} candidates...")
found = []
for c in candidates:
    r = requests.get(f"{dir_url}{c}")
    if r.status_code != 404 or "archive artifact not found" not in r.text:
        print(f"FOUND: {c} -> {r.status_code} ({len(r.content)} bytes)")
        found.append((c, r.status_code, r.content))
