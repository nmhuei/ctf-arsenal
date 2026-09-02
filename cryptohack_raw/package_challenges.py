#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

DEFAULT_ROOT = Path("cryptohack_challenges")


def load_metadata(challenge_dir: Path) -> dict:
    return json.loads((challenge_dir / "metadata.json").read_text(encoding="utf-8"))


def iter_challenge_dirs(root: Path):
    for meta_path in sorted(root.rglob("metadata.json")):
        yield meta_path.parent


def zip_name_for(challenge_dir: Path, root: Path) -> str:
    rel = challenge_dir.relative_to(root).as_posix()
    return rel.replace("/", "__") + ".zip"


def add_if_exists(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    if path.exists() and path.is_file():
        zf.write(path, arcname)


def package_challenge(challenge_dir: Path, root: Path, output: Path | None, inplace_name: str | None) -> Path:
    metadata = load_metadata(challenge_dir)
    if output is None:
        zip_filename = inplace_name or f"{metadata.get('slug') or challenge_dir.name}.zip"
        zip_path = challenge_dir / zip_filename
    else:
        output.mkdir(parents=True, exist_ok=True)
        zip_path = output / zip_name_for(challenge_dir, root)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        prefix = challenge_dir.name
        zf.writestr(
            f"{prefix}/README.txt",
            "\n".join(
                [
                    f"Title: {metadata.get('title', '')}",
                    f"Category: {metadata.get('category', '')}",
                    f"Stage: {metadata.get('stage', '')}",
                    f"Challenge ID: {metadata.get('data_challenge', '')}",
                    f"Points: {metadata.get('points', '')}",
                    "",
                ]
            ),
        )
        add_if_exists(zf, challenge_dir / "statement.md", f"{prefix}/statement.md")
        add_if_exists(zf, challenge_dir / "statement.html", f"{prefix}/statement.html")
        add_if_exists(zf, challenge_dir / "metadata.json", f"{prefix}/metadata.json")

        files_dir = challenge_dir / "files"
        if files_dir.exists():
            for file_path in sorted(p for p in files_dir.rglob("*") if p.is_file()):
                rel = file_path.relative_to(files_dir).as_posix()
                zf.write(file_path, f"{prefix}/files/{rel}")

    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Nen moi CryptoHack challenge thanh mot file zip.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Thu muc cryptohack_challenges.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Thu muc chua zip output. Mac dinh la tao zip ngay trong tung challenge.",
    )
    parser.add_argument(
        "--inplace-name",
        help="Ten file zip co dinh khi tao ngay trong tung challenge. Mac dinh dung slug challenge.",
    )
    parser.add_argument("--category", help="Chi nen category slug, vi du: aes.")
    args = parser.parse_args()

    if not args.root.exists():
        raise SystemExit(f"Khong tim thay root: {args.root}")

    count = 0
    total_size = 0
    for challenge_dir in iter_challenge_dirs(args.root):
        rel = challenge_dir.relative_to(args.root).as_posix()
        if args.category and not rel.startswith(args.category.strip("/") + "/"):
            continue
        zip_path = package_challenge(challenge_dir, args.root, args.output, args.inplace_name)
        count += 1
        total_size += zip_path.stat().st_size
        print(f"[{count}] {zip_path}")

    print(f"done: {count} zip files, {total_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
