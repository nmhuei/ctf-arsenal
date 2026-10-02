# 📌 Quy Tắc Tổ Chức Thư Mục (Workspace Guidelines)

- **`script/`**: Thư mục workspace nháp. Hãy viết toàn bộ script test, payload thử nghiệm, fuzzing, giải mã linh tinh tại đây để tránh làm rác thư mục gốc.
- **`solver/`**: Khi script giải bài hoàn thiện và lấy được flag thành công, hãy chuyển/lưu script chính thức vào thư mục `solver/` (ví dụ `solver/solve.py`).
- **`writeup/`**: Thư mục viết báo cáo, phân tích kỹ thuật và ghi lại Flag sau khi giải xong bài.

<!-- CTF-SOLVER-RULES:START -->
## CTF solver workflow

- Read `metadata.json` first, then `challenge/NOTE.md`.
- If source provides a service, build its local server or harness in `script/`. If no source exists, do not invent a local server.
- Put every probe, temporary parser, test harness, debug artifact and technical log in `script/`.
- Document analysis and findings in `script/analysis.md`.
- Keep the final reusable solver at `solver/solve.py`.
- Solve and verify locally first; use an instance only after local verification.
- After successful local verification, write `script/worker-report.json` with `{"local_verification":"passed","summary":"what was verified"}`.
- After saving flag to `flag.txt`: Write a thorough, step-by-step cognitive writeup to `writeup/README.md`.
  - Focus strictly on the actual thought process and discovery trail, NOT generic textbook theory:
    1. **Rationale**: Why this exact step was performed.
    2. **Discovery Triggers**: What specific clues, strings, xrefs, code patterns, or anomalies were detected that prompted that action.
    3. **Research Trail**: Exactly what was searched online (queries, docs, CVEs, RFCs, GitHub repositories) and how the findings were applied to this problem.
    4. **Dead-ends & Pivots**: What initial hypotheses failed and why you pivoted to the winning path.
<!-- CTF-SOLVER-RULES:END -->
