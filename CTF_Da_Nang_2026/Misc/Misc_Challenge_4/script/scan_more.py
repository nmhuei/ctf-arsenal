import requests
import time
import urllib3

urllib3.disable_warnings()
BASE_URL = "https://bbfbc1bf-5042-411e-86b4-29657887ee45.222.255.138.122.nip.io"
s = requests.Session()
s.verify = False

def req(method, path, **kwargs):
    time.sleep(1.8)
    while True:
        try:
            r = s.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
            if r.status_code == 502:
                time.sleep(2.5)
                continue
            return r
        except Exception as e:
            time.sleep(3.0)

static_files = [
    "/static/app.js",
    "/static/main.js",
    "/static/script.js",
    "/static/bundle.js",
    "/static/index.js",
    "/static/auth.js",
    "/static/api.js",
    "/static/favicon.ico",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/.env",
    "/.git/config",
    "/app.py",
    "/server.py",
    "/main.py",
]

print("--- Testing static / source files ---")
for f in static_files:
    r = req("GET", f)
    if r.status_code != 404:
        print(f"GET {f} -> {r.status_code} len={len(r.content)} {r.text[:80]}")

api_routes = [
    "/api/models",
    "/api/inference",
    "/api/generate",
    "/api/chat",
    "/api/predict",
    "/api/v1/models",
    "/api/v1/chat/completions",
    "/api/v1/completions",
    "/v1/models",
    "/v1/chat/completions",
    "/v1/completions",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/metrics",
    "/healthz",
]

print("\n--- Testing API routes with GET & POST ---")
for route in api_routes:
    r_get = req("GET", route)
    print(f"GET {route} -> {r_get.status_code} {r_get.text[:60]}")
    r_post = req("POST", route, json={})
    print(f"POST {route} -> {r_post.status_code} {r_post.text[:60]}")
