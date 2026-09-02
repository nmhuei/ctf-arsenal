#!/usr/bin/env python3
"""
Scanwich Station remote sender.

This is NOT a magic exploit generator. It converts a local payload that already
works against qrscan into the exact HTTP request used by the challenge service.

Supported inputs:
  1) --text TEXT
     Generates a benign QR PNG for path probing.

  2) --image exploit.png
     Sends a PNG you already generated locally.

  3) --raw-frame frame.bin
     Converts one or more qrscan frame records into concatenated greyscale PNGs.
     frame.bin format is exactly what qrscan reads from stdin:
         <uint32_le width><uint32_le height><width*height raw 8-bit pixels>
         [repeat...]
     This is useful when your local exploit is a raw qrscan stdin file.

Request sent:
    POST /scan?raw=1
    multipart/form-data:
        station=kitchen
        image=<PNG or concatenated PNG stream>
"""

from __future__ import annotations

import argparse
import io
import re
import struct
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")
MAX_HTTP_PREVIEW = 8000


def make_qr_png(text: str) -> bytes:
    try:
        import qrcode
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: qrcode\n"
            "Install with: python3 -m pip install 'qrcode[pil]' requests\n"
            "Or use --image / --raw-frame to avoid QR generation."
        ) from exc

    img = qrcode.make(text).convert("L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def frame_to_png(width: int, height: int, pixels: bytes) -> bytes:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: Pillow\n"
            "Install with: python3 -m pip install pillow requests\n"
        ) from exc

    if width <= 0 or height <= 0:
        raise ValueError(f"invalid frame dimensions: {width}x{height}")
    expected = width * height
    if len(pixels) != expected:
        raise ValueError(f"bad frame length: got {len(pixels)}, expected {expected}")

    img = Image.frombytes("L", (width, height), pixels)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def raw_frames_to_concatenated_png(raw: bytes) -> bytes:
    out = bytearray()
    off = 0
    idx = 0
    while off < len(raw):
        if off + 8 > len(raw):
            raise ValueError(f"truncated frame header at offset {off}")
        width, height = struct.unpack_from("<II", raw, off)
        off += 8
        n = width * height
        if off + n > len(raw):
            raise ValueError(
                f"truncated frame {idx}: {width}x{height}, "
                f"need {n} bytes, have {len(raw) - off}"
            )
        pixels = raw[off : off + n]
        off += n
        png = frame_to_png(width, height, pixels)
        out.extend(png)
        print(f"[+] converted raw frame {idx}: {width}x{height}, raw={n}, png={len(png)}")
        idx += 1

    if idx == 0:
        raise ValueError("no frames in raw input")
    return bytes(out)


def load_payload(args: argparse.Namespace) -> tuple[bytes, str, str]:
    selected = [bool(args.image), bool(args.raw_frame)]
    if sum(selected) > 1:
        raise SystemExit("Use only one of --image or --raw-frame")

    if args.image:
        path = Path(args.image)
        return path.read_bytes(), path.name, "custom PNG"

    if args.raw_frame:
        path = Path(args.raw_frame)
        data = raw_frames_to_concatenated_png(path.read_bytes())
        return data, path.with_suffix(".png").name, "raw qrscan frame converted to PNG"

    return make_qr_png(args.text), "ticket.png", "benign QR probe"


def post_scan(base_url: str, payload: bytes, filename: str, timeout: float, verify_tls: bool) -> requests.Response:
    endpoint = urljoin(base_url.rstrip("/") + "/", "scan?raw=1")
    files = {"image": (filename, payload, "image/png")}
    data = {"station": "kitchen"}
    return requests.post(endpoint, data=data, files=files, timeout=timeout, verify=verify_tls)


def main() -> int:
    ap = argparse.ArgumentParser(description="Send Scanwich local payload to remote /scan?raw=1")
    ap.add_argument("base_url", help="https://...gpn24.ctf.kitctf.de")
    ap.add_argument("--image", help="Exploit PNG/concatenated PNG produced locally")
    ap.add_argument("--raw-frame", help="Raw qrscan stdin frames: <u32 w><u32 h><pixels> repeated")
    ap.add_argument("--text", default="HELLO_FROM_KITCHEN", help="QR text for benign probe mode")
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("-k", "--insecure", action="store_true", help="Disable TLS verification")
    ap.add_argument("--save-response", default="scanwich_remote_response.txt")
    args = ap.parse_args()

    try:
        payload, filename, mode = load_payload(args)
    except Exception as exc:
        print(f"[-] payload preparation failed: {exc}", file=sys.stderr)
        return 2

    print(f"[+] target: {args.base_url.rstrip('/')}")
    print("[+] endpoint: /scan?raw=1")
    print("[+] form: station=kitchen")
    print(f"[+] mode: {mode}")
    print(f"[+] upload: {filename} ({len(payload)} bytes)")

    try:
        r = post_scan(args.base_url, payload, filename, args.timeout, not args.insecure)
    except requests.RequestException as exc:
        print(f"[-] request failed: {exc}", file=sys.stderr)
        return 2

    body = r.text
    Path(args.save_response).write_text(body, encoding="utf-8", errors="replace")

    print(f"[+] HTTP {r.status_code}")
    print(f"[+] response saved: {args.save_response}")
    print("----- response begin -----")
    preview = body[:MAX_HTTP_PREVIEW]
    print(preview, end="" if preview.endswith("\n") else "\n")
    if len(body) > MAX_HTTP_PREVIEW:
        print(f"... <truncated, total {len(body)} chars>")
    print("----- response end -----")

    flags = FLAG_RE.findall(body)
    if flags:
        print(f"[+] FLAG: {flags[0]}")
        return 0

    if mode == "benign QR probe" and args.text in body:
        print("[+] kitchen path confirmed on remote; this is only a benign probe, not a flag exploit.")
    else:
        print("[-] no flag found in response")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
