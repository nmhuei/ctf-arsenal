import os
import subprocess
import tempfile
import sys

def test_url(url, extra_flags=[]):
    profile = tempfile.mkdtemp(prefix="prof-")
    js_flags = "--no-memory-protection-keys --expose-cage-base"
    if extra_flags:
        js_flags += " " + " ".join(extra_flags)
    cmd = [
        "./script/candidate/chrome/chrome",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        f"--user-data-dir={profile}",
        "--enable-logging=stderr",
        f"--js-flags={js_flags}",
        url
    ]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = p.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
    for line in out.splitlines():
        if "CONSOLE" in line or "cage" in line.lower() or "maglev" in line.lower() or "error" in line.lower() or "fatal" in line.lower():
            print(line)

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/run_test.html"
    test_url(url)
