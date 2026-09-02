#!/usr/bin/env python3
"""Standalone live A/B timing verifier for two candidates and two controls."""

from __future__ import annotations

import argparse
import math
import statistics
import time
from collections.abc import Iterable

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MIN_INTERVAL_SECONDS = 3.0
TIMEOUT_SECONDS = 15.0


def median_mad(values: Iterable[float]) -> tuple[float, float]:
    data = list(values)
    if not data:
        raise ValueError("no latency samples")
    median = statistics.median(data)
    mad = statistics.median(abs(value - median) for value in data)
    return median, mad


def normal_upper_tail(z_score: float) -> float:
    return 0.5 * math.erfc(z_score / math.sqrt(2.0))


def rank_sum_greater(candidate: list[float], controls: list[float]) -> tuple[float, float]:
    """Return (one-sided p-value, U) for candidate > pooled controls."""
    if not candidate or not controls:
        raise ValueError("rank sum needs candidate and control samples")
    combined = [(value, 0) for value in candidate] + [(value, 1) for value in controls]
    combined.sort(key=lambda item: item[0])
    ranks = [0.0] * len(combined)
    index = 0
    while index < len(combined):
        end = index + 1
        while end < len(combined) and combined[end][0] == combined[index][0]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for rank_index in range(index, end):
            ranks[rank_index] = rank
        index = end
    n1 = len(candidate)
    n2 = len(controls)
    rank_sum = sum(rank for rank, (_, group) in zip(ranks, combined) if group == 0)
    u = rank_sum - n1 * (n1 + 1) / 2.0
    mean = n1 * n2 / 2.0
    tie_counts: dict[float, int] = {}
    for value, _group in combined:
        tie_counts[value] = tie_counts.get(value, 0) + 1
    tie_term = sum(count**3 - count for count in tie_counts.values())
    variance = n1 * n2 / 12.0 * (n1 + n2 + 1 - tie_term / ((n1 + n2) * (n1 + n2 - 1)))
    if variance <= 0:
        return (0.0 if u > mean else 1.0), u
    z_score = (u - mean - 0.5) / math.sqrt(variance)
    return normal_upper_tail(z_score), u


class Pacer:
    def __init__(self, interval: float = MIN_INTERVAL_SECONDS):
        self.interval = interval
        self.next_start = 0.0

    def wait_for_slot(self) -> None:
        remaining = self.next_start - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)

    def reserve(self) -> None:
        self.next_start = time.monotonic() + self.interval


def probe(endpoint: str, token: str, pacer: Pacer) -> float:
    pacer.wait_for_slot()
    pacer.reserve()
    started = time.perf_counter_ns()
    try:
        with requests.Session() as session:
            session.verify = False
            response = session.post(
                endpoint,
                json={"token": token},
                headers={"Connection": "close"},
                timeout=TIMEOUT_SECONDS,
            )
    except requests.RequestException as exc:
        raise RuntimeError(f"probe {token!r} failed: {exc}") from exc
    elapsed = (time.perf_counter_ns() - started) / 1_000_000.0
    if response.status_code not in (200, 401):
        print(f"  warning: {token!r} returned HTTP {response.status_code}")
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="target base URL")
    parser.add_argument("charA")
    parser.add_argument("charB")
    parser.add_argument("ctrl1")
    parser.add_argument("ctrl2")
    parser.add_argument("--rounds", type=int, default=12)
    args = parser.parse_args()
    if args.rounds < 2:
        parser.error("--rounds must be at least 2")

    endpoint = args.url.rstrip("/")
    if not endpoint.endswith("/api/authenticate"):
        endpoint += "/api/authenticate"
    labels = ("A", "B", "ctrl1", "ctrl2")
    tokens = (args.charA, args.charB, args.ctrl1, args.ctrl2)
    samples = {label: [] for label in labels}
    pacer = Pacer()
    print(f"[*] Endpoint: {endpoint}; rounds={args.rounds}; interval={pacer.interval:.1f}s")
    for round_number in range(1, args.rounds + 1):
        for label, token in zip(labels, tokens):
            samples[label].append(probe(endpoint, token, pacer))
        print(f"[round {round_number}/{args.rounds}] collected A/B/controls", flush=True)

    all_values = [value for values in samples.values() for value in values]
    global_median, global_mad = median_mad(all_values)
    elevated_threshold = global_median + max(25.0, 3.0 * global_mad)
    summaries: dict[str, tuple[float, float, float]] = {}
    for label in labels:
        median, mad = median_mad(samples[label])
        elevated_rate = sum(value > elevated_threshold for value in samples[label]) / args.rounds
        summaries[label] = median, mad, elevated_rate

    control_values = samples["ctrl1"] + samples["ctrl2"]
    control_medians = [summaries["ctrl1"][0], summaries["ctrl2"][0]]
    print(
        f"\nGlobal median/MAD: {global_median:.1f}/{global_mad:.1f} ms; "
        f"elevated threshold: {elevated_threshold:.1f} ms"
    )
    for label in labels:
        median, mad, rate = summaries[label]
        print(f"{label:5s} median={median:7.1f} ms MAD={mad:6.1f} ms elevated-rate={rate:.2f}")

    verdicts = []
    for label in ("A", "B"):
        p_value, u = rank_sum_greater(samples[label], control_values)
        median = summaries[label][0]
        above_controls = median > max(control_medians)
        signal = p_value <= 0.05 and above_controls
        verdicts.append(signal)
        print(
            f"rank-sum {label}: U={u:.1f}, one-sided p={p_value:.4f}, "
            f"above both controls={'yes' if above_controls else 'no'}"
        )

    if any(verdicts):
        print("\nGO: signal present; continue attack")
    else:
        print("\nNO-GO: no separation; keep watching")


if __name__ == "__main__":
    main()
