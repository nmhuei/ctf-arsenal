import json
import os

with open("cryptohack_flags.json") as f:
    data = json.load(f)
    
entries = data.get("entries", {})

with open("summary.md", "w") as out:
    out.write("# CryptoHack Challenges Status\n\n")
    out.write("| Challenge Path | Solved | Flag |\n")
    out.write("|---|---|---|\n")
    
    for path, info in entries.items():
        solved = "Yes" if info.get("solved") else "No"
        flag = info.get("flag", "")
        out.write(f"| {path} | {solved} | `{flag}` |\n")

print("Generated summary.md")
