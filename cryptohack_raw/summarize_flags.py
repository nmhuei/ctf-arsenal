from pathlib import Path

ROOT = Path("cryptohack_challenges/ctf-archive")
output_lines = []

for p in sorted(ROOT.rglob("flag.txt")):
    rel_path = p.relative_to(ROOT)
    try:
        flag = p.read_text(encoding="utf-8").strip()
    except Exception as e:
        flag = f"Error reading: {e}"
    output_lines.append(f"{rel_path}: {flag}")

Path("ctf_archive_flags_summary.txt").write_text("\n".join(output_lines) + "\n", encoding="utf-8")
print(f"Summarized {len(output_lines)} flags to ctf_archive_flags_summary.txt")
