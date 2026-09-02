import json
import os
from pathlib import Path

ROOT = Path("cryptohack_challenges")
STATE_PATH = Path("cryptohack_flags.json")

with open(STATE_PATH, "r") as f:
    state = json.load(f)

entries = state.get("entries", {})

unsolved_solvers = []
for p in sorted(ROOT.rglob("solve")):
    rel_key = p.parent.relative_to(ROOT).as_posix()
    entry = entries.get(rel_key, {})
    if not entry.get("solved") or not entry.get("flag"):
        # find any python or sage scripts in solve/
        files = [f.name for f in p.iterdir() if f.is_file()]
        unsolved_solvers.append((rel_key, p, files))

print(f"Found {len(unsolved_solvers)} unsolved challenges with a solve directory:")
for key, p, files in unsolved_solvers:
    print(f"- {key}: {files}")
