#!/usr/bin/env python3
"""Non-linear whitelist-safe jq features based on mktime/gmtime.

The outer jq stream item is [[position], codepoint] (or [[last_position]] for
the closing marker).  `flatten|mktime` interprets [position, codepoint] as a
partially specified calendar tuple.  libc normalisation couples both values
non-linearly, yielding much stronger position-character fingerprints than add.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Iterable

import solve_checked as base

LENGTH = 142
PRINTABLE = "".join(chr(value) for value in range(32, 127))


def days_from_civil(year: int, month: int, day: int) -> int:
    """Days since 1970-01-01 in the proleptic Gregorian calendar."""
    year -= 1 if month <= 2 else 0
    era = (year if year >= 0 else year - 399) // 400
    year_of_era = year - era * 400
    shifted_month = month + (-3 if month > 2 else 9)
    day_of_year = (153 * shifted_month + 2) // 5 + day - 1
    day_of_era = (
        year_of_era * 365
        + year_of_era // 4
        - year_of_era // 100
        + day_of_year
    )
    return era * 146097 + day_of_era - 719468


def model_mktime(values: Iterable[int]) -> int:
    fields = list(values) + [0] * 8
    year, month, day, hour, minute, second = fields[:6]
    year_delta, month = divmod(month, 12)
    year += year_delta
    return (
        days_from_civil(year, month + 1, 1) + day - 1
    ) * 86400 + hour * 3600 + minute * 60 + second


def model_gmtime(timestamp: int) -> list[int]:
    converted = time.gmtime(timestamp)
    return [
        converted.tm_year,
        converted.tm_mon - 1,
        converted.tm_mday,
        converted.tm_hour,
        converted.tm_min,
        converted.tm_sec,
        (converted.tm_wday + 1) % 7,
        converted.tm_yday - 1,
    ]


PERMUTATIONS: dict[str, tuple[str, Callable[[list[int]], list[int]]]] = {
    "r": ("reverse", lambda values: list(reversed(values))),
    "s": ("sort", lambda values: sorted(values)),
    "d": ("sort|reverse", lambda values: sorted(values, reverse=True)),
    "u": ("unique", lambda values: sorted(set(values))),
    "v": ("unique|reverse", lambda values: sorted(set(values), reverse=True)),
}


@dataclass(frozen=True)
class TimestampSource:
    name: str
    suffix: str
    sequence: tuple[str, ...]

    def evaluate(self, index: int, char: int | None) -> int:
        timestamp = model_mktime([index] if char is None else [index, char])
        for permutation in self.sequence:
            _, transform = PERMUTATIONS[permutation]
            timestamp = model_mktime(transform(model_gmtime(timestamp)))
        return timestamp


@dataclass(frozen=True)
class MktimeFeature:
    name: str
    suffix: str
    source: TimestampSource
    kind: str

    def evaluate(self, index: int, char: int | None) -> int:
        timestamp = self.source.evaluate(index, char)
        if self.kind.startswith("dec_"):
            return base.decimal_fingerprint(timestamp, self.kind[4:])
        if self.kind == "logb":
            return abs(timestamp).bit_length() - 1

        calendar = model_gmtime(timestamp)
        kind = self.kind[3:]
        if kind == "first":
            return calendar[0]
        if kind == "last":
            return calendar[-1]
        if kind == "min":
            return min(calendar)
        if kind == "max":
            return max(calendar)
        if kind == "add":
            return sum(calendar)
        if kind == "uniqadd":
            return sum(set(calendar))
        if kind == "len":
            return len(calendar)
        raise ValueError(kind)


def build_sources(depth: int = 2) -> list[TimestampSource]:
    base_suffix = "flatten|mktime"
    sources = [TimestampSource("m", base_suffix, ())]
    sequences: list[tuple[str, ...]] = [()]
    frontier = [()]
    for _ in range(depth):
        next_frontier: list[tuple[str, ...]] = []
        for prefix in frontier:
            for key in PERMUTATIONS:
                sequence = prefix + (key,)
                sequences.append(sequence)
                next_frontier.append(sequence)
        frontier = next_frontier

    for sequence in sequences[1:]:
        suffix = base_suffix
        for key in sequence:
            suffix += "|gmtime|" + PERMUTATIONS[key][0] + "|mktime"
        sources.append(TimestampSource("m" + "".join(sequence), suffix, sequence))
    return sources


def build_features(depth: int = 2) -> list[MktimeFeature]:
    decimal_kinds = ("len", "first", "last", "min", "max", "add")
    calendar_kinds = ("first", "last", "min", "max", "add", "uniqadd", "len")
    raw: list[MktimeFeature] = []

    for source in build_sources(depth):
        for kind in decimal_kinds:
            tail = (
                "|tostring|length"
                if kind == "len"
                else f"|tostring|explode|{kind}"
            )
            raw.append(
                MktimeFeature(
                    f"{source.name}_dec_{kind}",
                    source.suffix + tail,
                    source,
                    f"dec_{kind}",
                )
            )

        raw.append(
            MktimeFeature(
                f"{source.name}_logb",
                source.suffix + "|abs|logb",
                source,
                "logb",
            )
        )

        for kind in calendar_kinds:
            operation = {
                "first": "first",
                "last": "last",
                "min": "min",
                "max": "max",
                "add": "add",
                "uniqadd": "unique|add",
                "len": "length",
            }[kind]
            raw.append(
                MktimeFeature(
                    f"{source.name}_gm_{kind}",
                    source.suffix + "|gmtime|" + operation,
                    source,
                    f"gm_{kind}",
                )
            )
    return raw


def candidate_points(
    charset: str = PRINTABLE,
    length: int = LENGTH,
) -> list[tuple[int, int | None]]:
    points: list[tuple[int, int | None]] = []
    for position in range(length):
        for char in base.fixed_domain(position, length, charset):
            points.append((position, char))
    points.append((length - 1, None))
    return points


def deduplicate_features(
    features: list[MktimeFeature],
    points: list[tuple[int, int | None]],
) -> tuple[list[MktimeFeature], list[tuple[int, ...]]]:
    unique: list[MktimeFeature] = []
    tables: list[tuple[int, ...]] = []
    seen: dict[tuple[int, ...], str] = {}
    for feature in features:
        table = tuple(feature.evaluate(index, char) for index, char in points)
        if table in seen:
            continue
        seen[table] = feature.name
        unique.append(feature)
        tables.append(table)
    return unique, tables
