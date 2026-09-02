import subprocess

def run_jq(expr):
    cmd = ["jq", "-cn", expr]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

print("tostream output:")
print(run_jq('"jail{hello}" | explode | tostream'))

print("\nOnly arrays (paths):")
print(run_jq('"jail{hello}" | explode | tostream | select(type == "array")'))
