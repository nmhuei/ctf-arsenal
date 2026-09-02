#!/usr/bin/env python3
"""
Probe/verification helper for Scanwich Station.
It generates a valid QR code and submits it to /scan with station=kitchen.
This confirms the hidden kitchen path is reachable. It is not a full flag exploit.
"""
import argparse
import io
import sys

import qrcode
import requests


def make_qr_png(text: str) -> bytes:
    qr = qrcode.QRCode(border=4, box_size=8)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="base URL, e.g. http://127.0.0.1:5000")
    ap.add_argument("--text", default="SCANWICH_KITCHEN_PROBE")
    ap.add_argument("--station", default="kitchen", choices=["guest", "kitchen"])
    args = ap.parse_args()

    base = args.base.rstrip("/")
    png = make_qr_png(args.text)
    files = {"image": ("probe.png", png, "image/png")}
    data = {"station": args.station}
    r = requests.post(f"{base}/scan?raw=1", files=files, data=data, timeout=120)
    print(f"[+] HTTP {r.status_code}")
    print(r.text)
    if r.status_code == 200 and args.text in r.text:
        print("[+] proof: scanner decoded our controlled QR text")
        return 0
    print("[-] probe text not found in response")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
