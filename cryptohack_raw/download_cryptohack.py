#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md

BASE_URL = "https://cryptohack.org"
CHALLENGES_URL = f"{BASE_URL}/challenges/"


@dataclass
class Category:
    title: str
    slug: str
    url: str
    completed: str | None = None
    total: str | None = None


@dataclass
class Challenge:
    category: str
    category_slug: str
    stage: str
    stage_slug: str
    title: str
    slug: str
    data_challenge: str
    points: int | None
    solves: int | None
    url: str
    attachments: list[dict]
    resources: list[dict]


def slugify(value: str, fallback: str = "item") -> str:
    value = unquote(value).strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or fallback


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def ensure_cloakbrowser():
    try:
        from cloakbrowser import launch
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Thieu dependency cloakbrowser. Hay chay: pip install -r requirements.txt"
        ) from exc
    return launch


def read_page(page, url: str, delay: float) -> str:
    page.goto(url, wait_until="networkidle", timeout=90_000)
    if delay:
        time.sleep(delay)
    return page.content()


def parse_categories(html: str) -> list[Category]:
    soup = BeautifulSoup(html, "html.parser")
    categories: list[Category] = []
    for card in soup.select("ul.listCards > a[href^='/challenges/']"):
        href = card.get("href") or ""
        title_el = card.select_one("h4")
        if not href or not title_el:
            continue

        complete_text = clean_text(card.select_one(".cardComplete").get_text(" ")) if card.select_one(".cardComplete") else ""
        completed = total = None
        match = re.search(r"(\d+)\s*/\s*(\d+)", complete_text)
        if match:
            completed, total = match.groups()

        url = urljoin(BASE_URL, href)
        slug = slugify(urlparse(url).path.rstrip("/").split("/")[-1])
        categories.append(
            Category(
                title=clean_text(title_el.get_text(" ")),
                slug=slug,
                url=url,
                completed=completed,
                total=total,
            )
        )
    return categories


def parse_points_and_solves(header) -> tuple[int | None, int | None]:
    text = clean_text(header.get_text(" "))
    points_match = re.search(r"(\d+)\s+pts?", text)
    solves_match = re.search(r"(\d+)\s+Solves?", text)
    points = int(points_match.group(1)) if points_match else None
    solves = int(solves_match.group(1)) if solves_match else None
    return points, solves


def links_from_description(desc, download_only: bool) -> list[dict]:
    links: list[dict] = []
    for a in desc.select("a[href]"):
        href = a.get("href") or ""
        is_download = a.has_attr("download")
        if download_only and not is_download:
            continue
        if not download_only and is_download:
            continue
        links.append(
            {
                "text": clean_text(a.get_text(" ")),
                "href": href,
                "url": urljoin(BASE_URL, href),
                "download": is_download,
            }
        )
    return links


def parse_category_page(html: str, category: Category) -> tuple[dict, list[tuple[Challenge, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    description = soup.select_one(".categoryDescription")
    category_meta = {
        **asdict(category),
        "description_text": clean_text(description.get_text(" ")) if description else "",
        "stages": [],
    }

    results: list[tuple[Challenge, str]] = []
    for stage_el in soup.select("span.stage[data-stage]"):
        seen_slugs: set[str] = set()
        stage_slug = slugify(stage_el.get("data-stage") or "stage")
        stage_title_el = stage_el.select_one(".challengeInfo h4")
        stage_title = clean_text(stage_title_el.get_text(" ")) if stage_title_el else stage_slug
        category_meta["stages"].append({"title": stage_title, "slug": stage_slug})

        for li in stage_el.select("li.challenge"):
            header = li.select_one(".collapsible-header[data-challenge]")
            desc = li.select_one(".challengeDescription")
            title_el = li.select_one(".challenge-text")
            if not header or not desc or not title_el:
                continue

            data_challenge = str(header.get("data-challenge"))
            title = clean_text(title_el.get_text(" "))
            base_slug = slugify(title, data_challenge)
            challenge_slug = base_slug
            if challenge_slug in seen_slugs:
                challenge_slug = f"{base_slug}-{slugify(data_challenge)}"
            counter = 2
            while challenge_slug in seen_slugs:
                challenge_slug = f"{base_slug}-{counter}"
                counter += 1
            seen_slugs.add(challenge_slug)

            points, solves = parse_points_and_solves(header)
            attachments = links_from_description(desc, download_only=True)
            resources = links_from_description(desc, download_only=False)
            challenge = Challenge(
                category=category.title,
                category_slug=category.slug,
                stage=stage_title,
                stage_slug=stage_slug,
                title=title,
                slug=challenge_slug,
                data_challenge=data_challenge,
                points=points,
                solves=solves,
                url=category.url,
                attachments=attachments,
                resources=resources,
            )
            results.append((challenge, str(desc)))
    return category_meta, results


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for i in range(2, 10_000):
        candidate = path.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot find unique filename for {path}")


def filename_from_response(url: str, response) -> str:
    disposition = response.headers.get("content-disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', disposition, re.I)
    if match:
        return Path(unquote(match.group(1))).name
    name = Path(unquote(urlparse(url).path)).name
    return name or "attachment.bin"


def download_attachment(request_context, attachment: dict, files_dir: Path) -> dict:
    url = attachment["url"]
    response = request_context.get(url, timeout=120_000)
    if not response.ok:
        return {**attachment, "saved_as": None, "status": response.status}

    filename = slugify(filename_from_response(url, response), "attachment.bin")
    out_path = unique_path(files_dir / filename)
    out_path.write_bytes(response.body())
    return {
        **attachment,
        "saved_as": str(out_path.relative_to(files_dir.parent)),
        "status": response.status,
        "size": out_path.stat().st_size,
    }


def write_challenge(
    request_context,
    output_dir: Path,
    challenge: Challenge,
    description_html: str,
    download_files: bool,
) -> dict:
    challenge_dir = output_dir / challenge.category_slug / challenge.stage_slug / challenge.slug
    files_dir = challenge_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    (challenge_dir / "solve").mkdir(exist_ok=True)
    (challenge_dir / "writeup").mkdir(exist_ok=True)

    statement_html = BeautifulSoup(description_html, "html.parser").prettify()
    statement_md = html_to_md(statement_html, heading_style="ATX").strip() + "\n"

    downloaded = []
    if download_files:
        for attachment in challenge.attachments:
            downloaded.append(download_attachment(request_context, attachment, files_dir))

    metadata = asdict(challenge)
    metadata["attachments"] = downloaded if download_files else challenge.attachments
    metadata["statement_html"] = "statement.html"
    metadata["statement_md"] = "statement.md"

    (challenge_dir / "statement.html").write_text(statement_html, encoding="utf-8")
    (challenge_dir / "statement.md").write_text(statement_md, encoding="utf-8")
    (challenge_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def iter_limited(items: Iterable, limit: int | None):
    for index, item in enumerate(items):
        if limit is not None and index >= limit:
            break
        yield item


def main() -> int:
    parser = argparse.ArgumentParser(description="Download CryptoHack challenges with CloakBrowser.")
    parser.add_argument("--output", default="cryptohack_challenges", help="Output directory.")
    parser.add_argument("--headed", action="store_true", help="Show browser window.")
    parser.add_argument("--delay", type=float, default=0.25, help="Delay after each page load, seconds.")
    parser.add_argument("--limit-categories", type=int, help="Only process first N categories.")
    parser.add_argument("--limit-challenges", type=int, help="Only process first N challenges per category.")
    parser.add_argument("--no-files", action="store_true", help="Skip attachment downloads.")
    parser.add_argument(
        "--login-wait",
        action="store_true",
        help="Open the login page first and wait for Enter before scraping.",
    )
    args = parser.parse_args()

    launch = ensure_cloakbrowser()
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    browser = launch(headless=not args.headed, humanize=True)
    try:
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        if args.login_wait:
            page.goto(f"{BASE_URL}/login/", wait_until="networkidle", timeout=90_000)
            input("[*] Login in the browser window, then press Enter here to continue...")

        print(f"[*] Loading {CHALLENGES_URL}", flush=True)
        index_html = read_page(page, CHALLENGES_URL, args.delay)
        categories = parse_categories(index_html)
        if not categories:
            raise RuntimeError("Khong tim thay category nao tren trang challenges.")

        all_metadata = {"source": CHALLENGES_URL, "categories": []}
        for category in iter_limited(categories, args.limit_categories):
            print(f"[*] Category: {category.title} ({category.url})", flush=True)
            category_html = read_page(page, category.url, args.delay)
            category_meta, challenges = parse_category_page(category_html, category)

            category_dir = output_dir / category.slug
            category_dir.mkdir(parents=True, exist_ok=True)
            (category_dir / "category.html").write_text(category_html, encoding="utf-8")

            saved = []
            for challenge, desc_html in iter_limited(challenges, args.limit_challenges):
                print(f"    - {challenge.stage} / {challenge.title}", flush=True)
                saved.append(
                    write_challenge(
                        context.request,
                        output_dir,
                        challenge,
                        desc_html,
                        download_files=not args.no_files,
                    )
                )

            category_meta["challenge_count"] = len(saved)
            category_meta["challenges"] = [
                {
                    "title": c["title"],
                    "stage": c["stage"],
                    "path": f"{c['category_slug']}/{c['stage_slug']}/{c['slug']}",
                    "attachments": c["attachments"],
                }
                for c in saved
            ]
            (category_dir / "category.json").write_text(
                json.dumps(category_meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            all_metadata["categories"].append(category_meta)

        (output_dir / "index.json").write_text(
            json.dumps(all_metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[*] Done: {output_dir}", flush=True)
        return 0
    finally:
        browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
