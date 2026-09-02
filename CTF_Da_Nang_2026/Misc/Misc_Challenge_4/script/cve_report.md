# CVE Verification Report

- Target: `https://619b19eb-70d8-4eaf-ae1c-57d1c8de2a76.222.255.138.122.nip.io`
- Server: `nginx/1.30.4`
- Generated: 2026-08-23 18:43:09

| ID | Component | Check | Verdict | Evidence |
|---|---|---|---|---|
| INFO-TLS | tls | certificate fingerprint | **INFO** | sha256:dbd44495db324b7d510ad1c23c681a318347564a |
| CVE-2023-44487 | nginx | HTTP/2 Rapid Reset exposure | **MITIGATED** | ALPN=http/1.1; h2 not negotiated => rapid-reset surface absent |
| INFO-FRP | frp | frp vhost router fronting target | **NOT-AFFECTED** | no frp signature |
| CVE-2021-23017 | nginx | DNS resolver off-by-one | **PATCHED** | running 1.30.4, fixed >= 1.21.0 |
| CVE-2022-41741/42 | nginx | mp4 module overread | **PATCHED** | running 1.30.4, fixed >= 1.23.3 |
| CVE-2024-7347 | nginx | mp4 buffering overread | **PATCHED** | running 1.30.4, fixed >= 1.27.1 |
| CVE-2024-34069 | werkzeug | debugger PIN bypass / exposed console | **MITIGATED** | GET /console -> HTTP 404 |
| APP-CWE-20 | flask-app | type confusion crash on non-dict JSON body | **VULNERABLE** | array->500 int->500 null->400 |
| APP-CWE-209 | flask-app | error messages expose internals/debug mode | **MITIGATED** | malformed JSON -> HTTP 401, 98 bytes; generic error |
| NGX-TRAVERSAL | nginx | static route path traversal / alias misconfig | **MITIGATED** | all 4 variants blocked |
| NGX-MERGE-SLASHES | nginx | double-slash path handling | **INFO** | POST //api//authenticate -> HTTP 405 |
| HTTP-SMUGGLING | nginx | CL.TE / TE.CL desync probes | **MITIGATED** | CL+TE conflict->400; TE+CL conflict->400; TE obfuscation->400 |
| DUP-HOST | nginx | duplicate Host header handling | **MITIGATED** | duplicate Host -> HTTP 400 |
| HDR-LIMITS | nginx | oversized header handling | **MITIGATED** | 9KB header -> HTTP 400 |
| METHOD-TRACE | nginx | TRACE method enabled (XST) | **MITIGATED** | TRACE -> HTTP 405 |
| CVE-2023-30861 | flask | session cookie caching issue | **NOT-AFFECTED** | application sets no cookies |
