#!/usr/bin/env python3
"""CVE / vulnerability verification battery for the NeuroServe stack.

Stack under test: client -> nginx/1.30.4 (frp vhost tunnel) -> Flask/Werkzeug.

Non-destructive by design: single-shot probes only, no floods, no brute force.
Usage:
    python3 script/cve_check.py <base-url> [--report script/cve_report.md]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import ssl
import sys
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

C_OK = "\033[92m"
C_WARN = "\033[93m"
C_BAD = "\033[91m"
C_DIM = "\033[2m"
C_RST = "\033[0m"

COLOR = {
    "VULNERABLE": C_BAD,
    "UNKNOWN": C_WARN,
    "MITIGATED": C_OK,
    "PATCHED": C_OK,
    "NOT-AFFECTED": C_DIM,
    "INFO": C_DIM,
}

# Fixed-version map for the 2026 nginx advisories.  Keep the version-to-CVE
# relationship data-driven so a new nginx release only needs a table update.
NGINX_2026_CVES: dict[str, tuple[tuple[str, str], ...]] = {
    "1.30.1": (
        ("CVE-2026-42926", ""),
        ("CVE-2026-42945", ""),
        ("CVE-2026-42946", ""),
        ("CVE-2026-42934", ""),
        ("CVE-2026-40460", ""),
        ("CVE-2026-40701", ""),
    ),
    "1.30.2": (("CVE-2026-9256", ""),),
    "1.30.3": (
        ("CVE-2026-42055", ""),
        ("CVE-2026-48142", ""),
        ("CVE-2026-42530", "mainline"),
    ),
    "1.30.4": (
        ("CVE-2026-42533", ""),
        ("CVE-2026-60005", ""),
        ("CVE-2026-56434", ""),
    ),
}


@dataclass
class Finding:
    cve_id: str
    component: str
    title: str
    verdict: str
    evidence: str = ""

    def line(self) -> str:
        c = COLOR.get(self.verdict, "")
        ev = "\n        " + self.evidence.replace("\n", "\n        ") if self.evidence else ""
        return f"{c}[{self.verdict:>12}]{C_RST} {self.cve_id:<18} {self.component:<9} {self.title}{ev}"


def ver_gte(v: tuple[int, ...], fixed: tuple[int, ...]) -> bool:
    n = max(len(v), len(fixed))
    a = v + (0,) * (n - len(v))
    b = fixed + (0,) * (n - len(fixed))
    return a >= b


def raw_request(host: str, port: int, payload: bytes, timeout: float = 8.0):
    """Send raw bytes over TLS, return (status|None, head+body preview)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                tls.settimeout(timeout)
                tls.sendall(payload)
                buf = b""
                try:
                    while len(buf) < 16384:
                        d = tls.recv(4096)
                        if not d:
                            break
                        buf += d
                except socket.timeout:
                    pass
    except OSError as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)
    m = re.match(rb"HTTP/[0-9.]+ (\d{3})", buf)
    status = int(m.group(1)) if m else None
    return status, buf.decode("latin1", "replace")[:900]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--report", default="script/cve_report.md")
    args = ap.parse_args()

    base = args.url.rstrip("/")
    p = urlparse(base)
    host, scheme = p.hostname, p.scheme
    port = p.port or (443 if scheme == "https" else 80)

    findings: list[Finding] = []

    def add(cve: str, comp: str, title: str, verdict: str, evidence: str = "") -> None:
        f = Finding(cve, comp, title, verdict, evidence)
        findings.append(f)
        print(f.line(), flush=True)

    s = requests.Session()
    s.verify = False

    print("=== Target: %s ===" % base)

    # ------------------------------------------------------------- [0] probe
    print("\n--- [0] Reachability & fingerprint ---")
    try:
        r_home = s.get(base + "/", timeout=10)
    except requests.RequestException as exc:
        print("Target unreachable: %s" % exc)
        sys.exit(2)

    server_hdr = r_home.headers.get("Server", "?")
    m_ngx = re.search(r"nginx/([\d.]+)", server_hdr)
    ngx_ver = tuple(int(x) for x in m_ngx.group(1).split(".")) if m_ngx else None
    print("Server header : %s" % server_hdr)
    print("GET /         : HTTP %s, %d bytes" % (r_home.status_code, len(r_home.text)))
    print("Content-Type  : %s" % r_home.headers.get("Content-Type", "?"))

    # TLS cert fingerprint
    try:
        pem = ssl.get_server_certificate((host, port)).encode()
        add("INFO-TLS", "tls", "certificate fingerprint",
            "INFO", "sha256:" + hashlib.sha256(pem).hexdigest()[:40])
    except OSError as exc:
        add("INFO-TLS", "tls", "certificate inspection failed", "UNKNOWN", str(exc))

    # ALPN / HTTP-2 support
    alpn = None
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_alpn_protocols(["h2", "http/1.1"])
        with socket.create_connection((host, port), timeout=8) as sk:
            with ctx.wrap_socket(sk, server_hostname=host) as t:
                alpn = t.selected_alpn_protocol()
    except OSError as exc:
        add("CVE-2023-44487", "nginx", "ALPN probe failed", "UNKNOWN", str(exc))
    if alpn is not None:
        add("CVE-2023-44487", "nginx", "HTTP/2 Rapid Reset exposure",
            "MITIGATED" if alpn != "h2" else "UNKNOWN",
            "ALPN=%s; h2 not negotiated => rapid-reset surface absent" % alpn
            if alpn != "h2" else "ALPN=h2 -> depends on nginx http2 config")

    # frp tunnel signature on unknown vhost path
    r404 = s.get(base + "/no-such-route-xyz-123", timeout=10)
    frp_sig = "frp" in r404.text or "fatedier" in r404.text
    add("INFO-FRP", "frp", "frp vhost router fronting target",
        "INFO" if frp_sig else "NOT-AFFECTED",
        "frp 404 page signature" if frp_sig else "no frp signature")

    # ------------------------------------------------- [1] version-based CVEs
    print("\n--- [1] Version-based applicability ---")
    if ngx_ver:
        running = ".".join(map(str, ngx_ver))
        for fixed_text, cves in NGINX_2026_CVES.items():
            fixed = tuple(int(part) for part in fixed_text.split("."))
            for cve, track in cves:
                title = "nginx 2026 security advisory"
                if track:
                    title += " (" + track + ")"
                add(
                    cve,
                    "nginx",
                    title,
                    "PATCHED" if ver_gte(ngx_ver, fixed) else "APPLICABLE",
                    "running %s, fixed >= %s%s"
                    % (running, fixed_text, "; " + track if track else ""),
                )
    else:
        add("INFO-NGINX", "nginx", "version undisclosed", "UNKNOWN", "Server: " + server_hdr)

    # --------------------------------------------------- [2] active app probes
    print("\n--- [2] Active probes ---")

    auth = base + "/api/authenticate"

    def post(token_payload, timeout=12):
        return s.post(auth, json=token_payload, timeout=timeout)

    # Werkzeug debug console (CVE-2024-34069 family requires debugger enabled)
    r_con = s.get(base + "/console", timeout=10)
    dbg_on = r_con.status_code == 200 and ("console" in r_con.text.lower())
    add("CVE-2024-34069", "werkzeug", "debugger PIN bypass / exposed console",
        "VULNERABLE" if dbg_on else "MITIGATED",
        "GET /console -> HTTP %d%s" % (r_con.status_code,
                                       ", console frame present" if dbg_on else ""))

    # Type confusion / unhandled exception (app-level CWE-20, known bug)
    st_arr = post(["000000000000000000000000000000000000000000000000"]).status_code
    st_int = post(12345).status_code
    st_null = post({"token": None}).status_code
    add("APP-CWE-20", "flask-app", "type confusion crash on non-dict JSON body",
        "VULNERABLE" if {st_arr, st_int} & {500} else "MITIGATED",
        "array->%d int->%d null->%d" % (st_arr, st_int, st_null))

    # Verbose error leakage
    r_bad = s.post(auth, data='{"token": ', headers={"Content-Type": "application/json"},
                   timeout=10)
    leaks_werkzeug = "Traceback" in r_bad.text or "werkzeug" in r_bad.text.lower()
    add("APP-CWE-209", "flask-app", "error messages expose internals/debug mode",
        "VULNERABLE" if leaks_werkzeug else "MITIGATED",
        "malformed JSON -> HTTP %d, %d bytes%s" % (
            r_bad.status_code, len(r_bad.text),
            "; traceback leaked" if leaks_werkzeug else "; generic error"))

    # Path traversal via static route (nginx alias/off-by-slash class)
    trav_cases = {
        "alias off-by-slash": "/static../etc/passwd",
        "encoded dotdot": "/static/%2e%2e/%2e%2e/etc/passwd",
        "double encoded": "/static/%252e%252e/etc/passwd",
        "raw dotdot": "/static/../../../etc/passwd",
    }
    trav_hits = []
    for name, path in trav_cases.items():
        rt = s.get(base + path, timeout=10)
        if rt.status_code == 200 and ("root:" in rt.text):
            trav_hits.append("%s (%s)" % (name, path))
    add("NGX-TRAVERSAL", "nginx", "static route path traversal / alias misconfig",
        "VULNERABLE" if trav_hits else "MITIGATED",
        "; ".join(trav_hits) if trav_hits else "all %d variants blocked" % len(trav_cases))

    # Double-slash normalization confusion
    r_ds = s.post(auth.replace("://", "://") + "", json={"token": "0" * 48},
                  timeout=10) if False else None  # placeholder keep-alive reuse
    r_norm = s.request(
        "POST",
        base + "//api//authenticate",
        json={"token": "0" * 48}, timeout=10)
    add("NGX-MERGE-SLASHES", "nginx", "double-slash path handling",
        "INFO", "POST //api//authenticate -> HTTP %d" % r_norm.status_code)

    # Request smuggling: conflicting framing headers
    tok48 = "0" * 48
    body = '{"token":"%s"}' % tok48
    smuggle_cases = {
        "CL+TE conflict":
            b"Content-Length: " + str(len(body)).encode() + b"\r\nTransfer-Encoding: chunked\r\n",
        "TE+CL conflict":
            b"Transfer-Encoding: chunked\r\nContent-Length: " + str(len(body)).encode() + b"\r\n",
        "TE obfuscation":
            b"Transfer-Encoding: chunked\r\nX: y\r\nTransfer-Encoding: x\r\n",
    }
    smuggle_notes = []
    for name, extra in smuggle_cases.items():
        payload = (
            b"POST /api/authenticate HTTP/1.1\r\nHost: " + host.encode() + b"\r\n"
            + extra +
            b"Content-Type: application/json\r\nConnection: close\r\n\r\n"
            + body.encode()
        )
        st, preview = raw_request(host, port, payload)
        smuggle_notes.append("%s->%s" % (name, st))
        if st == 200:
            add("SMUGGLE-" + name.split()[0], "nginx", "framing conflict forwarded",
                "VULNERABLE", preview)
    add("HTTP-SMUGGLING", "nginx", "CL.TE / TE.CL desync probes",
        "MITIGATED" if all(not n.endswith("->200") for n in smuggle_notes) else "VULNERABLE",
        "; ".join(smuggle_notes))

    # Duplicate Host header
    dup_host_status, _ = raw_request(
        host, port,
        b"POST /api/authenticate HTTP/1.1\r\nHost: " + host.encode()
        + b"\r\nHost: evil.example.com\r\nContent-Length: "
        + str(len(body)).encode()
        + b"\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n"
        + body.encode())
    add("DUP-HOST", "nginx", "duplicate Host header handling",
        "MITIGATED" if dup_host_status == 400 else "INFO",
        "duplicate Host -> HTTP %s" % dup_host_status)

    # Oversized header line (default nginx large_client_header_buffers=8k)
    big_status, _ = raw_request(
        host, port,
        b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\nX-Big: "
        + b"A" * 9000 + b"\r\nConnection: close\r\n\r\n")
    add("HDR-LIMITS", "nginx", "oversized header handling",
        "MITIGATED" if big_status == 400 or big_status == 494 else "INFO",
        "9KB header -> HTTP %s" % big_status)

    # TRACE method (XST)
    r_trace = s.request("TRACE", base + "/", timeout=10)
    add("METHOD-TRACE", "nginx", "TRACE method enabled (XST)",
        "VULNERABLE" if r_trace.status_code == 200 else "MITIGATED",
        "TRACE -> HTTP %d" % r_trace.status_code)

    # Session cookie flags (Flask CVE-2023-30861 context)
    cookie_hdr = r_home.headers.get("Set-Cookie", "")
    if cookie_hdr:
        flags_ok = "httponly" in cookie_hdr.lower() and "secure" in cookie_hdr.lower()
        add("CVE-2023-30861", "flask", "session cookie without protection headers",
            "MITIGATED" if flags_ok else "VULNERABLE", "Set-Cookie: " + cookie_hdr[:120])
    else:
        add("CVE-2023-30861", "flask", "session cookie caching issue",
            "NOT-AFFECTED", "application sets no cookies")

    # ---------------------------------------------------------------- report
    print("\n=== SUMMARY ===")
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.verdict] = counts.get(f.verdict, 0) + 1
    for k, v in sorted(counts.items()):
        print("%s%12s%s : %d" % (COLOR.get(k, ""), k, C_RST, v))

    md = ["# CVE Verification Report", "",
          "- Target: `%s`" % base,
          "- Server: `%s`" % server_hdr,
          "- Generated: %s" % time.strftime("%Y-%m-%d %H:%M:%S"), "",
          "| ID | Component | Check | Verdict | Evidence |",
          "|---|---|---|---|---|"]
    for f in findings:
        md.append("| %s | %s | %s | **%s** | %s |" % (
            f.cve_id, f.component, f.title.replace("|", "\\|"),
            f.verdict, (f.evidence or "").replace("|", "\\|").replace("\n", " ")))
    from pathlib import Path
    Path(args.report).write_text("\n".join(md) + "\n")
    print("\nReport saved to %s" % args.report)


if __name__ == "__main__":
    main()
