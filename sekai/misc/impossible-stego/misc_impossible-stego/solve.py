import json
import base64
import shutil
from pathlib import Path

LOG = "messages.log"
PROJECT_ROOT = "/home/claude/projects/impossible-stego/"
OUT_DIR = Path("recovered_source")


def parse_sse(text: str):
    blocks = {}

    for part in text.split("\n\n"):
        data_lines = []
        for line in part.splitlines():
            if line.startswith("data:"):
                data_lines.append(line[5:].strip())

        if not data_lines:
            continue

        data = "\n".join(data_lines)

        try:
            obj = json.loads(data)
        except Exception:
            continue

        typ = obj.get("type")

        if typ == "content_block_start":
            idx = obj["index"]
            cb = obj.get("content_block", {})

            block = {
                "type": cb.get("type"),
                "name": cb.get("name"),
                "id": cb.get("id"),
                "input_json": "",
                "text": cb.get("text", ""),
            }

            if cb.get("input"):
                block["input_json"] = json.dumps(cb["input"])

            blocks[idx] = block

        elif typ == "content_block_delta":
            idx = obj["index"]
            delta = obj.get("delta", {})
            block = blocks.setdefault(idx, {})

            if delta.get("type") == "input_json_delta":
                block["input_json"] = block.get("input_json", "") + delta.get("partial_json", "")

            elif delta.get("type") == "text_delta":
                block["text"] = block.get("text", "") + delta.get("text", "")

    result = []

    for idx in sorted(blocks):
        block = blocks[idx]

        if block.get("input_json"):
            try:
                block["input"] = json.loads(block["input_json"])
            except Exception as e:
                block["input_error"] = str(e)

        result.append(block)

    return result


files = {}
ops = []

with open(LOG, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        obj = json.loads(line)
        encoded = obj.get("resp_body")

        if not encoded:
            continue

        try:
            decoded = base64.b64decode(encoded).decode("utf-8", "replace")
        except Exception:
            continue

        for block in parse_sse(decoded):
            if block.get("type") != "tool_use":
                continue

            name = block.get("name")
            inp = block.get("input", {})
            fp = inp.get("file_path", "")

            if not fp:
                continue

            rel = fp[len(PROJECT_ROOT):] if fp.startswith(PROJECT_ROOT) else fp

            if rel.startswith("/"):
                continue

            if name == "Write":
                files[rel] = inp["content"]
                ops.append((line_no, "Write", rel))

            elif name == "Edit":
                if rel not in files:
                    ops.append((line_no, "Edit missing", rel))
                    continue

                old = inp["old_string"]
                new = inp["new_string"]
                replace_all = inp.get("replace_all", False)

                count = files[rel].count(old)

                if replace_all:
                    files[rel] = files[rel].replace(old, new)
                else:
                    files[rel] = files[rel].replace(old, new, 1)

                ops.append((line_no, "Edit", rel, count))

            elif name == "MultiEdit":
                if rel not in files:
                    ops.append((line_no, "MultiEdit missing", rel))
                    continue

                for edit in inp.get("edits", []):
                    old = edit["old_string"]
                    new = edit["new_string"]
                    replace_all = edit.get("replace_all", False)

                    if replace_all:
                        files[rel] = files[rel].replace(old, new)
                    else:
                        files[rel] = files[rel].replace(old, new, 1)

                ops.append((line_no, "MultiEdit", rel))


if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)

for rel, content in files.items():
    path = OUT_DIR / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

print("[+] recovered files:", len(files))
for op in ops:
    print(op)
