#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path


TAG_RE = re.compile(r"(?s)<[^>]+>")


def text_from_html(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    txt = TAG_RE.sub("\n", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t\r\f\v]+", " ", txt)
    txt = re.sub(r"\n\s+", "\n", txt)
    return txt.strip()


def compact(txt: str) -> str:
    return re.sub(r"\s+", " ", txt).strip()


def main() -> None:
    terms = re.compile(
        r"unknown321|A\. Reza|protonmail|Reza|Rajesh|Patel|RPC|account|bank|"
        r"beneficiary|routing|swift|iban|ifsc|wire|settlement|receipt|external|"
        r"150K|150,000|SK-PRIVATE",
        re.I,
    )
    paths = sorted(Path("evidence").glob("mail*.html"))
    for path in paths:
        if path.name.startswith("mail_search_"):
            continue
        txt = text_from_html(path.read_text(errors="replace"))
        if not terms.search(txt):
            continue
        lines = [compact(line) for line in txt.splitlines() if compact(line)]
        interesting = [line for line in lines if terms.search(line)]
        subject = next((line for line in lines if line and "FirstBangla Mail" not in line), "")
        print(f"\n=== {path} ===")
        print(f"SUBJECT_OR_FIRST: {subject[:220]}")
        for line in interesting[:18]:
            print(line[:260])


if __name__ == "__main__":
    main()
