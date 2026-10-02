#!/usr/bin/env python3
"""Exhaustive byte-operator search for the TASK.md system."""

from __future__ import annotations

import json
from itertools import product
from math import gcd
from pathlib import Path
from typing import Callable, Iterable


VECTOR_X = [
    148, 88, 81, 94, 43, 78, 234, 229, 13, 241, 74, 191,
    43, 77, 122, 170, 85, 84, 253, 202, 167, 60, 12, 18,
]
VECTOR_Y = [
    79, 113, 58, 140, 206, 198, 72, 196, 38, 165, 124, 48,
    199, 35, 98, 192, 237, 163, 234, 40, 252, 195, 152, 69,
]
CONSTANTS = {
    "phi1": "i",
    "phi2": 255,
    "phi3": 67,
    "phi4": 4,
}
OUTPUT_PATH = Path(__file__).resolve().with_name("solution.json")


def byte(value: int) -> int:
    return value & 0xFF


def rol(value: int, count: int) -> int:
    shift = count & 7
    value &= 0xFF
    if shift == 0:
        return value
    return ((value << shift) | (value >> (8 - shift))) & 0xFF


def ror(value: int, count: int) -> int:
    shift = count & 7
    value &= 0xFF
    if shift == 0:
        return value
    return ((value >> shift) | (value << (8 - shift))) & 0xFF


def swap_nibbles(value: int, _constant: int) -> int:
    value &= 0xFF
    return ((value & 0x0F) << 4) | ((value & 0xF0) >> 4)


class Operator:
    def __init__(
        self,
        name: str,
        apply: Callable[[int, int], int],
        valid: Callable[[Iterable[int]], bool] | None = None,
    ) -> None:
        self.name = name
        self.apply = apply
        self.valid = valid or (lambda _constants: True)

    def __repr__(self) -> str:
        return f"Operator({self.name!r})"


def candidate_operators() -> list[Operator]:
    return [
        Operator("identity", lambda v, _c: byte(v)),
        Operator("add", lambda v, c: byte(v + c)),
        Operator("sub", lambda v, c: byte(v - c)),
        Operator("rsub", lambda v, c: byte(c - v)),
        Operator("xor", lambda v, c: byte(v ^ c)),
        Operator("rol", lambda v, c: rol(v, c)),
        Operator("ror", lambda v, c: ror(v, c)),
        Operator("mul", lambda v, c: byte(v * c), lambda cs: all(gcd(c, 256) == 1 for c in cs)),
        Operator("not", lambda v, _c: byte(~v)),
        Operator("swap_nibbles", swap_nibbles),
        Operator("shl", lambda v, c: byte(v << (c & 7))),
        Operator("shr", lambda v, c: byte(v >> (c & 7))),
    ]


def constants_for_stage(stage_name: str) -> list[int]:
    constant = CONSTANTS[stage_name]
    if constant == "i":
        return list(range(len(VECTOR_X)))
    return [int(constant)]


def operators_for_stage(stage_name: str) -> list[Operator]:
    constants = constants_for_stage(stage_name)
    return [op for op in candidate_operators() if op.valid(constants)]


def apply_one(value: int, operator: Operator, constant: int) -> int:
    return byte(operator.apply(value, constant))


def apply_mapping(operators: list[str] | tuple[str, str, str, str], vector_x: list[int]) -> list[int]:
    by_name = {op.name: op for op in candidate_operators()}
    op1, op2, op3, op4 = [by_name[name] for name in operators]
    output = []
    for index, start in enumerate(vector_x):
        value = apply_one(start, op1, index)
        value = apply_one(value, op2, 255)
        value = apply_one(value, op3, 67)
        value = apply_one(value, op4, 4)
        output.append(value)
    return output


def mismatch_count(operators: tuple[Operator, Operator, Operator, Operator]) -> int:
    observed = apply_mapping(tuple(op.name for op in operators), VECTOR_X)
    return sum(actual != expected for actual, expected in zip(observed, VECTOR_Y))


def enumerate_solutions() -> list[dict[str, object]]:
    stage_ops = [
        operators_for_stage("phi1"),
        operators_for_stage("phi2"),
        operators_for_stage("phi3"),
        operators_for_stage("phi4"),
    ]
    solutions = []
    for ops in product(*stage_ops):
        observed = apply_mapping(tuple(op.name for op in ops), VECTOR_X)
        matched = sum(actual == expected for actual, expected in zip(observed, VECTOR_Y))
        if observed == VECTOR_Y:
            solutions.append(
                {
                    "operators": [op.name for op in ops],
                    "matched": matched,
                    "mismatches": 0,
                    "constants": CONSTANTS,
                }
            )
    return solutions


def best_candidates(limit: int = 10) -> list[dict[str, object]]:
    stage_ops = [
        operators_for_stage("phi1"),
        operators_for_stage("phi2"),
        operators_for_stage("phi3"),
        operators_for_stage("phi4"),
    ]
    ranked: list[tuple[int, tuple[Operator, Operator, Operator, Operator]]] = []
    for ops in product(*stage_ops):
        ranked.append((mismatch_count(ops), ops))
    ranked.sort(key=lambda item: item[0])
    return [
        {
            "operators": [op.name for op in ops],
            "matched": len(VECTOR_X) - mismatches,
            "mismatches": mismatches,
        }
        for mismatches, ops in ranked[:limit]
    ]


def search_summary() -> dict[str, object]:
    stage_operator_names = {
        stage: [op.name for op in operators_for_stage(stage)]
        for stage in ("phi1", "phi2", "phi3", "phi4")
    }
    tuple_count = 1
    for names in stage_operator_names.values():
        tuple_count *= len(names)
    solutions = enumerate_solutions()
    return {
        "status": "solved" if solutions else "no_exact_mapping",
        "operator_count": len(candidate_operators()),
        "stage_operator_names": stage_operator_names,
        "tested_tuple_count": tuple_count,
        "solutions": solutions,
        "selected_solution": solutions[0] if solutions else None,
        "best_candidates": best_candidates(),
    }


def main() -> int:
    summary = search_summary()
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "solved" else 1


if __name__ == "__main__":
    raise SystemExit(main())
