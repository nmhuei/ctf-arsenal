import subprocess
import string
import solve_remote_live, json

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}
FEATURES = solve_remote_live.FEATURES

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def simulate_local_query(expr, flag):
    cmd = ["jq", "-n", expr]
    res = subprocess.run(cmd, capture_output=True, env={"FLAG": flag})
    if res.returncode != 0:
        return "error"
    return "ok"

def solve_local(test_flag):
    length = len(test_flag)
    charset = string.ascii_lowercase + string.digits + "_{}"
    
    recovered = ["?"] * length
    print(f"[*] Solving locally for test flag: '{test_flag}' (length {length})")

    for pos in range(length):
        matches = []
        for c in charset:
            v = ord(c)
            matched = False
            
            # 1. Forward add: pos + v
            val_fwd = pos + v
            if val_fwd in CHAINS:
                pred = predicate(CHAINS[val_fwd])
                expr = f"[env|flatten|sort|last|explode|tostream]|.[{pos}]|flatten|add|{pred}|error"
                if simulate_local_query(expr, test_flag) == "error":
                    matches.append(c)
                    continue

            # 2. Reverse add: (length - 1 - pos) + v
            val_rev = (length - 1 - pos) + v
            if val_rev in CHAINS:
                pred = predicate(CHAINS[val_rev])
                expr = f"[env|flatten|sort|last|explode|reverse|implode|explode|tostream]|.[{pos}]|flatten|add|{pred}|error"
                if simulate_local_query(expr, test_flag) == "error":
                    matches.append(c)
                    continue

            # 3. Multi-feature fallback for missing chains
            for fi in range(1, 20):
                feat = FEATURES[fi]
                v_feat = feat.evaluate(pos, v)
                if v_feat in CHAINS:
                    pred = predicate(CHAINS[v_feat])
                    expr = f"[env|flatten|sort|last|explode|tostream]|.[{pos}]|{feat.suffix}|{pred}|error"
                    if simulate_local_query(expr, test_flag) == "error":
                        matches.append(c)
                        matched = True
                        break

        if len(matches) == 1:
            recovered[pos] = matches[0]
            print(f"[+] Pos {pos:2d}: '{matches[0]}' -> {''.join(recovered)}")
        elif len(matches) > 1:
            print(f"[!] Pos {pos:2d}: ambiguous {matches}")
        else:
            print(f"[-] Pos {pos:2d}: no match found")

    result_flag = "".join(recovered)
    print(f"\n[+] Local solve result: {result_flag}")
    assert result_flag == test_flag, f"Mismatch: expected {test_flag!r}, got {result_flag!r}"
    print("="*80)
    print("[+] 100% PERFECT LOCAL VERIFICATION PASSED WITH ZERO MISSING CHARACTERS!")
    print("="*80)

if __name__ == "__main__":
    solve_local("jail{flag_will_be_here_on_remote}")
