import check_remote, solve_remote_live, json

chains = {int(k): v for k, v in json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON).items()}

print("Verifying base expressions and lengths...")

# Expressions to test for flag
bases = [
    "env|flatten|sort|last",
    "env|flatten|sort|first",
    "env|values|flatten|sort|last",
    "env|values|flatten|sort|first",
]

for b in bases:
    matches = []
    for val in sorted(chains.keys()):
        pred = solve_remote_live.predicate(chains[val])
        expr = f"{b}|length|{pred}|error"
        res = check_remote.query(expr)
        if res == "error":
            matches.append(val)
    print(f"Base: {b} -> length matches: {matches}")
