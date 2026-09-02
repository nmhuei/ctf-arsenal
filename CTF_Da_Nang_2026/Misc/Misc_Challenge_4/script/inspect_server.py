import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

r = s.get(f"{BASE_URL}/", timeout=10)
print("=== GET / ===")
print("Status:", r.status_code)
print("Headers:", dict(r.headers))
print("Cookies:", r.cookies.get_dict())

r_status = s.get(f"{BASE_URL}/api/status", timeout=10)
print("\n=== GET /api/status ===")
print("Status:", r_status.status_code)
print("Headers:", dict(r_status.headers))
print("Body:", r_status.text)
