import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

for i in range(10):
    r = s.post(f"{BASE_URL}/api/authenticate", json={"token": "0"*48}, timeout=10)
    print(f"Req {i}: status={r.status_code}, server={r.headers.get('Server')}, date={r.headers.get('Date')}, body={r.text[:60]}")
