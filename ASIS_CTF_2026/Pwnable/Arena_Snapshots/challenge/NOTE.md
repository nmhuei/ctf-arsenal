# Workspace rules

<!-- CTF-SOLVER-RULES:START -->
## CTF solver workflow

- Read `metadata.json` first, then `challenge/NOTE.md`.
- If source provides a service, build its local server or harness in `script/`. If no source exists, do not invent a local server.
- Put every probe, temporary parser, test harness, debug artifact and technical log in `script/`.
- Document analysis and findings in `script/analysis.md`.
- Keep the final reusable solver at `solver/solve.py`.
- Solve and verify locally first; use an instance only after local verification.
- After successful local verification, write `script/worker-report.json` with `{"local_verification":"passed","summary":"what was verified"}`.
<!-- CTF-SOLVER-RULES:END -->
