"""
Analyze the Ghost_Zero pcap - contains admin bootstrap auth flow.
Extract and decode all HTTP bodies to understand the legacy auth mechanism.
"""
import json
import base64
import subprocess

# First get the deleted Ghost_Zero pcap entry from DB
from client import GhostClient
c = GhostClient()
c.bootstrap()

# Check for the Ghost_Zero entry  
res = c.request("search", {"q": "' UNION SELECT id, cast(id as text), r4 FROM q_8f3c1a72d90e4b65 WHERE r4 LIKE '%Ghost_Zero%'--"})
if res.get("ok"):
    rows = [r for r in res["data"]["rows"] if r["id"] == 1]
    for r in rows:
        try:
            meta = json.loads(r["summary"])
            print("Ghost_Zero entry:", json.dumps(meta, indent=2))
        except:
            pass

# Now parse the pcap we already downloaded
print("\n" + "=" * 60)
print("Parsing ghost_zero.pcap HTTP bodies")
print("=" * 60)

out = subprocess.check_output([
    "tshark", "-r", "ghost_zero.pcap", "-Y", "http",
    "-T", "fields",
    "-e", "http.request.method",
    "-e", "http.request.uri",
    "-e", "http.response.code",
    "-e", "http.file_data"
], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')

for i, line in enumerate(out.strip().split('\n')):
    parts = line.split('\t')
    method = parts[0] if len(parts) > 0 else ""
    uri = parts[1] if len(parts) > 1 else ""
    status = parts[2] if len(parts) > 2 else ""
    hex_data = parts[3] if len(parts) > 3 else ""
    
    if hex_data:
        try:
            body = bytes.fromhex(hex_data).decode('utf-8')
            body_json = json.loads(body)
            
            desc = f"{'REQ' if method else 'RESP'} {method} {uri} {status}"
            print(f"\n--- Frame {i+1}: {desc} ---")
            print(json.dumps(body_json, indent=2))
            
            # Decode any JWT tokens found
            for key in ["token", "exchangeTicket", "ticket"]:
                if key in body_json:
                    tok = body_json[key]
                    tok_parts = tok.split('.')
                    if len(tok_parts) >= 2:
                        header = json.loads(base64.urlsafe_b64decode(tok_parts[0] + '=='))
                        payload = json.loads(base64.urlsafe_b64decode(tok_parts[1] + '=='))
                        sig_raw = base64.urlsafe_b64decode(tok_parts[2] + '==') if len(tok_parts) > 2 else b''
                        print(f"\n  >>> JWT {key} decoded:")
                        print(f"      Header:  {json.dumps(header)}")
                        print(f"      Payload: {json.dumps(payload)}")
                        print(f"      Sig:     {sig_raw}")
                        print(f"      Sig hex: {sig_raw.hex()}")
        except Exception as e:
            print(f"Frame {i+1}: decode error: {e}")
