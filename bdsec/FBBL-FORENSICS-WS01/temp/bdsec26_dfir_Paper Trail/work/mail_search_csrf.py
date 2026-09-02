#!/usr/bin/env python3
"""Search the webmail for specific terms - with CSRF token handling."""
import requests, time, sys, os, re

BASE = "http://50.116.30.77:5000"
SESSION = requests.Session()

# Step 1: GET login page to get CSRF token
r = SESSION.get(f"{BASE}/login", timeout=10)
m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.text)
if not m:
    print("ERROR: No CSRF token found"); sys.exit(1)
csrf = m.group(1)
print(f"CSRF token: {csrf[:40]}...")

# Step 2: POST login with CSRF
r = SESSION.post(f"{BASE}/login", data={
    "csrf_token": csrf,
    "email": "arif.khan@firstbangla.com",
    "password": "knightsquad4041337@"
}, allow_redirects=True, timeout=30)
print(f"Login status: {r.status_code}, URL: {r.url}")
if "Sign in" in r.text and "Inbox" not in r.text:
    print("WARNING: Login may have failed")
    # Try checking if we can access inbox
    r2 = SESSION.get(f"{BASE}/mail/inbox", timeout=10)
    if "Sign in" in r2.text:
        print("ERROR: Not logged in")
        sys.exit(1)
    else:
        print("OK: Logged in (redirect worked)")

# Step 3: Search for terms
terms = [
    "HDFC",
    "ICICI",
    "SBI",
    "State Bank",
    "Canara",
    "PNB",
    "Union Bank",
    "bank account",
    "account number",
    "RPC Consulting",
    "Rajesh",
    "invoice",
    "receipt",
    "beneficiary",
    "remittance",
    "payment receipt",
    "transfer receipt",
    "consulting",
    "Patel",
    "Mumbai",
    "commission",
    "fee payment",
    "external",
    "SK-PRIVATE",
    "private transfer",
    "cut",
    "20 percent",
    "SWIFT",
    "IBAN",
    "IFSC",
    "NEFT",
    "RTGS",
    "hawala",
    "150000",
    "$150",
    "500000",
    "$500",
    "Dubai",
    "City Trust",
    "CityTrust",
]

out_dir = "evidence"
for term in terms:
    slug = term.replace(' ', '_').replace('$', 'USD').replace('%','pct')[:40]
    try:
        r = SESSION.get(f"{BASE}/mail/search", params={"q": term}, timeout=30)
        m = re.search(r'(\d+) result\(s\)', r.text)
        count = int(m.group(1)) if m else -1
        if count > 0:
            outf = os.path.join(out_dir, f"search4_{slug}.html")
            with open(outf, "w") as f:
                f.write(r.text)
            # Extract result snippets
            snippets = re.findall(r'<p class="mail-snippet"[^>]*>(.*?)</p>', r.text, re.DOTALL)
            print(f"[HIT] '{term}' -> {count} results")
            for s in snippets[:3]:
                clean = re.sub('<[^>]+>', '', s).strip()
                print(f"  >> {clean[:200]}")
        else:
            print(f"[---] '{term}' -> 0 results")
        time.sleep(0.3)
    except Exception as e:
        print(f"[ERR] '{term}' -> {e}")
        time.sleep(2)

print("\nDone!")
