#!/usr/bin/env python3
"""Search the webmail for specific terms and save results."""
import requests, time, sys, os

BASE = "http://50.116.30.77:5000"
SESSION = requests.Session()

# Login
r = SESSION.post(f"{BASE}/login", data={
    "email": "arif.khan@firstbangla.com",
    "password": "knightsquad4041337@"
}, allow_redirects=True, timeout=30)
print(f"Login status: {r.status_code}")

terms = [
    "bank account",
    "HDFC",
    "ICICI",
    "State Bank",
    "SBI",
    "Canara",
    "PNB",
    "Union Bank",
    "RPC Consulting",
    "account number",
    "Rajesh Patel bank",
    "Mumbai bank",
    "external account",
    "beneficiary account",
    "receiving account",
    "wire transfer receipt",
    "transfer receipt",
    "NEFT",
    "RTGS",
    "consulting fee",
    "consulting invoice",
    "RPC invoice",
    "Patel invoice",
    "commission",
    "SK-PRIVATE",
    "Salim bank",
    "Salim account",
    "150000",
    "150,000",
    "$150",
    "cut",
    "20 percent",
    "crypto exchange",
    "mixing fee",
    "SWIFT code",
    "IBAN",
    "IFSC",
    "remittance",
    "hawala",
    "Arif Khan transfer",
    "Arif external",
]

out_dir = "evidence"
for term in terms:
    slug = term.replace(' ', '_').replace('$', 'USD')[:40]
    try:
        r = SESSION.get(f"{BASE}/mail/search", params={"q": term}, timeout=30)
        # Check if there are actual results (not "0 result(s)")
        if "0 result(s)" not in r.text and r.status_code == 200:
            outf = os.path.join(out_dir, f"search3_{slug}.html")
            with open(outf, "w") as f:
                f.write(r.text)
            # Count results
            import re
            m = re.search(r'(\d+) result\(s\)', r.text)
            count = m.group(1) if m else "?"
            print(f"[HIT] '{term}' -> {count} results -> {outf}")
        else:
            print(f"[---] '{term}' -> 0 results")
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERR] '{term}' -> {e}")
        time.sleep(2)

print("\nDone!")
