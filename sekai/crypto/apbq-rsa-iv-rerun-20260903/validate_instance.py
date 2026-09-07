import ast
import json
from pathlib import Path

source = Path("apbq-rsa-iv.py").read_text()
tree = ast.parse(source)
blocks = [x.value.value for x in tree.body if isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant) and isinstance(x.value.value, str)]
assert blocks
embedded = ast.parse(blocks[-1])
source_values = {x.targets[0].id: ast.literal_eval(x.value) for x in embedded.body if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name) and x.targets[0].id in {"n", "c", "hints"}}
instance = json.loads(Path("INSTANCE.json").read_text())
assert set(instance) == {"n", "c", "hints"}
assert type(instance["n"]) is int
assert type(instance["c"]) is int
assert type(instance["hints"]) is list
assert len(instance["hints"]) == 3
assert all(type(x) is int for x in instance["hints"])
assert instance["n"] > 0
assert instance["c"] >= 0
assert all(x >= 0 for x in instance["hints"])
assert instance["n"] == source_values["n"]
assert instance["c"] == source_values["c"]
assert instance["hints"] == source_values["hints"]
print("PASS: INSTANCE.json format, size, and source-value checks")
