#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path("cryptohack_challenges")
DEFAULT_STATE = Path("cryptohack_flags.json")


@dataclass
class Challenge:
    key: str
    category: str
    category_slug: str
    stage: str
    stage_slug: str
    title: str
    slug: str
    data_challenge: str
    points: int | None
    path: Path


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def scan_challenges(root: Path) -> list[Challenge]:
    if not root.exists():
        raise SystemExit(f"Khong tim thay thu muc dataset: {root}")

    challenges: list[Challenge] = []
    for meta_path in sorted(root.rglob("metadata.json")):
        data = load_json(meta_path, {})
        rel_dir = meta_path.parent.relative_to(root).as_posix()
        challenges.append(
            Challenge(
                key=rel_dir,
                category=data.get("category", ""),
                category_slug=data.get("category_slug", rel_dir.split("/", 1)[0]),
                stage=data.get("stage", ""),
                stage_slug=data.get("stage_slug", ""),
                title=data.get("title", meta_path.parent.name),
                slug=data.get("slug", meta_path.parent.name),
                data_challenge=data.get("data_challenge", ""),
                points=data.get("points"),
                path=meta_path.parent,
            )
        )
    return challenges


def empty_state() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": None,
        "entries": {},
    }


def normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
    state = empty_state()
    state.update(raw or {})
    state.setdefault("entries", {})
    return state


def get_entry(state: dict[str, Any], key: str) -> dict[str, Any]:
    return state.setdefault("entries", {}).setdefault(
        key,
        {
            "solved": False,
            "flag": "",
            "note": "",
            "updated_at": None,
        },
    )


def is_solved(state: dict[str, Any], challenge: Challenge) -> bool:
    entry = state.get("entries", {}).get(challenge.key, {})
    return bool(entry.get("solved") or entry.get("flag"))


def matches_filter(challenge: Challenge, state: dict[str, Any], args: argparse.Namespace) -> bool:
    if getattr(args, "category", None) and args.category.lower() not in {
        challenge.category.lower(),
        challenge.category_slug.lower(),
    }:
        return False
    if getattr(args, "stage", None):
        needle = args.stage.lower()
        if needle not in challenge.stage.lower() and needle != challenge.stage_slug.lower():
            return False
    if getattr(args, "search", None):
        haystack = " ".join(
            [
                challenge.key,
                challenge.category,
                challenge.stage,
                challenge.title,
                challenge.data_challenge,
            ]
        ).lower()
        if args.search.lower() not in haystack:
            return False
    status = getattr(args, "status", "all")
    solved = is_solved(state, challenge)
    if status == "solved" and not solved:
        return False
    if status == "unsolved" and solved:
        return False
    return True


def resolve_challenge(challenges: list[Challenge], query: str) -> Challenge:
    query = query.strip().lower().strip("/")
    exact = [
        c
        for c in challenges
        if query
        in {
            c.key.lower(),
            c.data_challenge.lower(),
            c.slug.lower(),
            c.title.lower(),
        }
    ]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        print_ambiguous(exact)
        raise SystemExit(2)

    fuzzy = [
        c
        for c in challenges
        if query in c.key.lower()
        or query in c.title.lower()
        or query in c.data_challenge.lower()
    ]
    if len(fuzzy) == 1:
        return fuzzy[0]
    if not fuzzy:
        raise SystemExit(f"Khong tim thay challenge match: {query}")
    print_ambiguous(fuzzy[:25])
    if len(fuzzy) > 25:
        print(f"... va {len(fuzzy) - 25} ket qua khac")
    raise SystemExit(2)


def print_ambiguous(items: list[Challenge]) -> None:
    print("Query bi trung, hay dung key day du hon:")
    for c in items:
        print(f"  {c.key}  [{c.data_challenge}]  {c.title}")


def short(value: str, width: int) -> str:
    value = value.replace("\n", " ")
    if len(value) <= width:
        return value
    return value[: max(0, width - 3)] + "..."


def print_table(rows: list[dict[str, Any]], show_flag: bool) -> None:
    headers = ["status", "key", "id", "pts", "title"]
    widths = [8, 54, 18, 5, 34]
    if show_flag:
        headers.append("flag")
        widths.append(38)

    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        values = [
            row["status"],
            row["key"],
            row["id"],
            str(row["points"] or ""),
            row["title"],
        ]
        if show_flag:
            values.append(row.get("flag", ""))
        print("  ".join(short(v, w).ljust(w) for v, w in zip(values, widths)))


def row_for(challenge: Challenge, state: dict[str, Any]) -> dict[str, Any]:
    entry = state.get("entries", {}).get(challenge.key, {})
    return {
        "status": "solved" if is_solved(state, challenge) else "unsolved",
        "key": challenge.key,
        "id": challenge.data_challenge,
        "category": challenge.category,
        "stage": challenge.stage,
        "title": challenge.title,
        "points": challenge.points,
        "flag": entry.get("flag", ""),
        "note": entry.get("note", ""),
        "updated_at": entry.get("updated_at"),
    }


def cmd_stats(challenges: list[Challenge], state: dict[str, Any], args: argparse.Namespace) -> int:
    filtered = [c for c in challenges if matches_filter(c, state, args)]
    solved = [c for c in filtered if is_solved(state, c)]
    total_points = sum(c.points or 0 for c in filtered)
    solved_points = sum(c.points or 0 for c in solved)
    print(f"total:          {len(filtered)}")
    print(f"solved:         {len(solved)}")
    print(f"unsolved:       {len(filtered) - len(solved)}")
    print(f"points solved:  {solved_points}/{total_points}")

    by_category: dict[str, list[Challenge]] = {}
    for c in filtered:
        by_category.setdefault(c.category_slug, []).append(c)
    if len(by_category) > 1:
        print()
        for category, items in sorted(by_category.items()):
            count = sum(1 for c in items if is_solved(state, c))
            print(f"{category:18} {count:3}/{len(items):3}")
    return 0


def cmd_list(challenges: list[Challenge], state: dict[str, Any], args: argparse.Namespace) -> int:
    filtered = [c for c in challenges if matches_filter(c, state, args)]
    if args.limit is not None:
        filtered = filtered[: args.limit]
    rows = [row_for(c, state) for c in filtered]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print_table(rows, show_flag=args.show_flag)
    return 0


def cmd_show(challenges: list[Challenge], state: dict[str, Any], args: argparse.Namespace) -> int:
    challenge = resolve_challenge(challenges, args.query)
    row = row_for(challenge, state)
    row["path"] = str(challenge.path)
    row["statement_md"] = str(challenge.path / "statement.md")
    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


def cmd_set(challenges: list[Challenge], state: dict[str, Any], args: argparse.Namespace) -> int:
    challenge = resolve_challenge(challenges, args.query)
    entry = get_entry(state, challenge.key)
    if args.flag is not None:
        entry["flag"] = args.flag.strip()
    if args.note is not None:
        entry["note"] = args.note.strip()
    entry["solved"] = True
    entry["updated_at"] = now_iso()
    state["updated_at"] = entry["updated_at"]
    save_json(args.state, state)
    print(f"saved: {challenge.key}")
    return 0


def cmd_unset(challenges: list[Challenge], state: dict[str, Any], args: argparse.Namespace) -> int:
    challenge = resolve_challenge(challenges, args.query)
    entry = get_entry(state, challenge.key)
    entry["solved"] = False
    if args.clear_flag:
        entry["flag"] = ""
    entry["updated_at"] = now_iso()
    state["updated_at"] = entry["updated_at"]
    save_json(args.state, state)
    print(f"unsolved: {challenge.key}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quan ly flag/solved status cho dataset CryptoHack offline.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Thu muc cryptohack_challenges.")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="File luu flag/status.")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_filters(p: argparse.ArgumentParser) -> None:
        p.add_argument("--category", help="Loc theo category slug/title, vi du: aes, rsa.")
        p.add_argument("--stage", help="Loc theo stage slug/title.")
        p.add_argument("--search", help="Tim trong key/title/id.")
        p.add_argument("--status", choices=["all", "solved", "unsolved"], default="all")

    p_stats = sub.add_parser("stats", help="Thong ke solved/unsolved.")
    add_filters(p_stats)
    p_stats.set_defaults(func=cmd_stats)

    p_list = sub.add_parser("list", help="Liet ke challenge.")
    add_filters(p_list)
    p_list.add_argument("--limit", type=int, help="Gioi han so dong in ra.")
    p_list.add_argument("--show-flag", action="store_true", help="In ca flag trong bang.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Xem chi tiet 1 challenge.")
    p_show.add_argument("query", help="Key/path, data_challenge, title hoac substring duy nhat.")
    p_show.set_defaults(func=cmd_show)

    p_set = sub.add_parser("set", help="Danh dau solved va luu flag/ghi chu.")
    p_set.add_argument("query", help="Key/path, data_challenge, title hoac substring duy nhat.")
    p_set.add_argument("flag", nargs="?", help="Flag tim duoc, vi du: crypto{...}")
    p_set.add_argument("--note", help="Ghi chu cach giai.")
    p_set.set_defaults(func=cmd_set)

    p_unset = sub.add_parser("unset", help="Danh dau chua solved.")
    p_unset.add_argument("query", help="Key/path, data_challenge, title hoac substring duy nhat.")
    p_unset.add_argument("--clear-flag", action="store_true", help="Xoa flag da luu.")
    p_unset.set_defaults(func=cmd_unset)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    challenges = scan_challenges(args.root)
    state = normalize_state(load_json(args.state, empty_state()))
    return args.func(challenges, state, args)


if __name__ == "__main__":
    raise SystemExit(main())
