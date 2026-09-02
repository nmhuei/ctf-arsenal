"""
Download and analyze ALL pcap files from the database.
Look for any additional endpoints, tokens, or flag material.
"""
import requests
import subprocess
import json
import base64

BASE = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

pcaps = [
    ("frontdesk-health", "/test/7f9c18a2e44d/5d0185499f64d3116843ddcb3dd16344.pcap"),
    ("guest-session-help", "/test/7f9c18a2e44d/04f9654471407af9db118e1cb7333bba.pcap"),
    ("desktop-searches", "/test/7f9c18a2e44d/73cfa9f8eafad4b574970ae9ced11c67.pcap"),
    ("mobile-searches", "/test/7f9c18a2e44d/d418e1a02f2f607a3d0f23a3cc1b9091.pcap"),
    ("ghost-zero", "/test/7f9c18a2e44d/fe291443882d55af94bff1f9cddffb73.pcap"),
]

for label, path in pcaps:
    fname = f"pcap_{label}.pcap"
    print(f"\n{'='*60}")
    print(f"=== {label} ({path}) ===")
    print(f"{'='*60}")
    
    r = requests.get(f"{BASE}{path}")
    if r.status_code != 200:
        print(f"  Failed to download: {r.status_code}")
        continue
    
    with open(fname, "wb") as f:
        f.write(r.content)
    
    # Extract HTTP data
    out = subprocess.check_output([
        "tshark", "-r", fname, "-Y", "http",
        "-T", "fields",
        "-e", "http.request.method",
        "-e", "http.request.uri",
        "-e", "http.response.code",
        "-e", "http.file_data",
        "-e", "http.request.full_uri"
    ], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
    
    for i, line in enumerate(out.strip().split('\n')):
        if not line.strip():
            continue
        parts = line.split('\t')
        method = parts[0] if len(parts) > 0 else ""
        uri = parts[1] if len(parts) > 1 else ""
        status = parts[2] if len(parts) > 2 else ""
        hex_data = parts[3] if len(parts) > 3 else ""
        full_uri = parts[4] if len(parts) > 4 else ""
        
        if hex_data:
            try:
                body = bytes.fromhex(hex_data).decode('utf-8')
                body_json = json.loads(body)
                
                desc = f"{'REQ' if method else 'RESP'} {method} {uri} {status}"
                if full_uri:
                    desc += f" ({full_uri})"
                print(f"\n  Frame {i+1}: {desc}")
                print(f"  Body: {json.dumps(body_json, indent=4)[:500]}")
                
                # Decode any JWT tokens
                for key in ["token", "exchangeTicket", "ticket"]:
                    if key in body_json:
                        tok = body_json[key]
                        tok_parts = tok.split('.')
                        if len(tok_parts) >= 2:
                            header = json.loads(base64.urlsafe_b64decode(tok_parts[0] + '=='))
                            payload = json.loads(base64.urlsafe_b64decode(tok_parts[1] + '=='))
                            print(f"    JWT {key}:")
                            print(f"      Header:  {json.dumps(header)}")
                            print(f"      Payload: {json.dumps(payload)}")
            except Exception as e:
                pass
