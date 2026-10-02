#!/usr/bin/env python3
"""Challenge bot: reads a URL from stdin and visits it with headless Chrome.

Only http/https URLs are accepted. The flag is /flag (mode 600, owned by ctf).
"""
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlparse

CHROME = os.environ.get("CHROME", "/home/ctf/chrome/chrome")
VISIT_SECONDS = int(os.environ.get("VISIT_SECONDS", "45"))


def main():
    sys.stdout.write("URL to visit (http/https only): ")
    sys.stdout.flush()
    url = sys.stdin.readline().strip()
    if urlparse(url).scheme.lower() not in ("http", "https"):
        print("rejected: only http/https URLs are allowed")
        return
    profile = tempfile.mkdtemp(prefix="prof-")
    cmd = [
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", f"--user-data-dir={profile}",
        "--js-flags=--no-memory-protection-keys --expose-cage-base", url,
    ]
    print(f"visiting {url} for {VISIT_SECONDS}s ...", flush=True)
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        t0 = time.time()
        while time.time() - t0 < VISIT_SECONDS and p.poll() is None:
            time.sleep(0.5)
    finally:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        # Always reclaim the per-visit profile. /tmp is a tmpfs; leaking one
        # profile per submission eventually fills it, after which Chrome aborts
        # in InitializeSharedMemoryRegions before running the page at all.
        shutil.rmtree(profile, ignore_errors=True)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
