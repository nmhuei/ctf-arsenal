import hashlib

pcap_hashes = [
    "5d0185499f64d3116843ddcb3dd16344",
    "04f9654471407af9db118e1cb7333bba",
    "73cfa9f8eafad4b574970ae9ced11c67",
    "d418e1a02f2f607a3d0f23a3cc1b9091",
    "fe291443882d55af94bff1f9cddffb73",
]

wordlist = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "frontdesk", "health", "index", "guest", "help", "desktop", "mobile",
    "ghost", "zero", "ghost_zero", "ghost-zero", "flag", "admin", "root",
    "ops-root", "legacy", "bootstrap", "ticket", "exchange", "d3ctf", "d3ctf2026",
    "capture", "traffic", "test", "archive"
]

for w in wordlist:
    h = hashlib.md5(w.encode()).hexdigest()
    if h in pcap_hashes:
        print(f"MATCH: md5({repr(w)}) == {h}")
