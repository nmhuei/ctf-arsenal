#!/usr/bin/env python3
"""Offline behavioral checks for solver/solve.py; intentionally pytest-free."""

from __future__ import annotations

import contextlib
import io
import random
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import solver.solve as solver


class FakeResponse:
    def __init__(self, status_code: int = 401, text: str = "fake"):
        self.status_code = status_code
        self.text = text


class _FakeMonitor:
    @staticmethod
    def relative_latency(latency_ms: float) -> float:
        return latency_ms


class FakeClient:
    """Small ResilientClient substitute with deterministic injectable timing."""

    def __init__(
        self,
        url: str,
        config: solver.ClientConfig,
        latency_fn: Callable[[str, int, int], float] | None = None,
    ):
        self.url = url
        self.config = config
        self.delay = config.delay
        self.endpoint = url.rstrip("/") + "/api/authenticate"
        self.monitor = _FakeMonitor()
        self.latency_fn = latency_fn or (lambda _token, _call, _char_call: 33.0)
        self.call_count = 0
        self.calls: list[tuple[str, float]] = []
        self._per_char_calls: dict[str, int] = {}

    def send_auth(self, token: str) -> tuple[float, FakeResponse]:
        self.call_count += 1
        char = token[0] if token else ""
        char_call = self._per_char_calls.get(char, 0) + 1
        self._per_char_calls[char] = char_call
        latency = float(self.latency_fn(token, self.call_count, char_call))
        self.calls.append((token, latency))
        return latency, FakeResponse(status_code=401)


def _run_recovery(
    fake: FakeClient,
    *,
    charset: str,
    state_path: Path,
) -> str:
    with contextlib.redirect_stdout(io.StringIO()):
        return solver.recover(
            "http://offline.invalid",
            config=solver.ClientConfig(delay=3.0),
            state_path=state_path,
            positions=1,
            verify_samples=4,
            accept_margin=12.0,
            charset=charset,
            rescreen_every=0,
            watch=False,
            client_factory=lambda _url, _config: fake,
        )


def test_clean_signal() -> None:
    rng = random.Random(1001)
    winner = "m"

    def latency(token: str, _call: int, _char_call: int) -> float:
        return 33.0 + rng.gauss(0.0, 3.0) + (70.0 if token[0] == winner else 0.0)

    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        fake = FakeClient("http://offline.invalid", solver.ClientConfig(), latency)
        recovered = _run_recovery(fake, charset=solver.CHARSET, state_path=Path(temp) / "state.json")
    assert recovered == winner
    assert fake.call_count <= 300
    print(f"CLEAN SIGNAL: selected {recovered!r} in {fake.call_count} probes")


def test_flicker_signal() -> None:
    winner = "m"
    elevated_pattern = [True, True, False, False, True, True, False, False, True, True]

    def latency(token: str, _call: int, char_call: int) -> float:
        elevated = token[0] == winner and elevated_pattern[(char_call - 1) % len(elevated_pattern)]
        return 33.0 + (80.0 if elevated else 0.0)

    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        fake = FakeClient("http://offline.invalid", solver.ClientConfig(), latency)
        recovered = _run_recovery(fake, charset=solver.CHARSET, state_path=Path(temp) / "state.json")
    assert recovered == winner
    assert fake.call_count <= 400
    print(f"FLICKER SIGNAL: selected {recovered!r} in {fake.call_count} probes")


def test_no_signal() -> None:
    rng = random.Random(2002)

    def latency(_token: str, _call: int, _char_call: int) -> float:
        if rng.random() < 0.02:
            return 800.0
        return 33.0 + rng.gauss(0.0, 3.0)

    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        state_path = Path(temp) / "state.json"
        fake = FakeClient("http://offline.invalid", solver.ClientConfig(), latency)
        try:
            _run_recovery(fake, charset=solver.CHARSET, state_path=state_path)
        except solver.NoWinner as exc:
            assert exc.best_z is None or exc.best_z >= 0.0
        else:
            raise AssertionError("random-spike no-signal stream produced a winner")
        if state_path.exists():
            state = solver.load_state(state_path, "http://offline.invalid")
            assert state.get("recovered", "") == ""
            assert state.get("positions", []) == []
    original_recover = solver.recover
    original_argv = sys.argv[:]

    def no_winner_recover(*_args, **_kwargs):
        raise solver.NoWinner("synthetic no-signal")

    solver.recover = no_winner_recover  # type: ignore[assignment]
    sys.argv = ["solve.py", "http://offline.invalid", "--positions", "1"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                solver.main()
            except SystemExit as exc:
                assert exc.code == 5
            else:
                raise AssertionError("CLI did not exit 5 for NoWinner")
    finally:
        solver.recover = original_recover  # type: ignore[assignment]
        sys.argv = original_argv
    print(f"NO SIGNAL: reached NoWinner path after {fake.call_count} probes; state clean")


def test_artifact_guard() -> None:
    assert not solver.artifact_guard_accepts(8.5, [33.0, 34.0], 33.0, 3.0)
    assert solver.artifact_guard_accepts(8.5, [70.0, 72.0], 33.0, 3.0)
    print("ARTIFACT GUARD: flat outlier excluded; two elevated re-probes lead")


def test_sprt() -> None:
    rng = random.Random(3003)
    true_samples = [rng.gauss(103.0, 3.0) for _ in range(12)]
    null_samples = [rng.gauss(33.0, 3.0) for _ in range(12)]
    true_result = solver.sprt_decision(true_samples, 33.0, 70.0, 3.0)
    null_result = solver.sprt_decision(null_samples, 33.0, 70.0, 3.0)
    assert true_result[0] == "accept" and true_result[1] <= 12
    assert null_result[0] == "reject" and null_result[1] <= 12
    print(f"SPRT: true accepted in n={true_result[1]}; null rejected in n={null_result[1]}")


def test_cadence_controller() -> None:
    config = solver.ClientConfig(delay=6.0, min_delay=3.0, max_delay=15.0)
    client = solver.ResilientClient("http://offline.invalid", config)
    initial = client.delay
    for number in range(12):
        client._record_attempt(401, 33.0, float(number))
    after_success = client.delay
    for number in range(12, 24):
        client._record_attempt(503, 33.0, float(number))
    after_failure = client.delay
    assert after_success < initial
    assert after_failure > after_success
    assert config.min_delay <= after_failure <= config.max_delay
    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        path = Path(temp) / "cadence.json"
        solver.save_state(path, {"cadence": round(after_failure, 3)})
        loaded = solver.load_state(path, "http://offline.invalid")
    assert loaded["cadence"] == round(after_failure, 3)
    print(
        f"CADENCE: success {initial:.2f}->{after_success:.2f}s; "
        f"failures -> {after_failure:.2f}s; persisted"
    )


def test_accumulated_flicker_signal() -> None:
    """A winner that flickers twice across three screens must be promoted."""
    winner = "m"
    # Seven older samples make the ninth total sample eligible for the
    # historical-prime threshold; only two of the three new screens spike.
    seed_state = {
        "url": "http://offline.invalid",
        "recovered": "",
        "positions": [],
        "evidence": {
            "1": {winner: {"n": 7, "elev": 1, "sum_ms": 231.0}}
        },
        "cadence": None,
        "winner_delta_band": [],
    }

    spike_calls: list[int] = []
    screen_passes: list[int] = []

    def latency(token: str, _call: int, char_call: int) -> float:
        # With dual-pass screening, the first three screens contribute two
        # samples for m each; the first and fourth are elevated.
        if token[0] == winner and char_call in range(1, 7):
            screen_passes.append(char_call)
        if token[0] == winner and char_call in (1, 4):
            spike_calls.append(char_call)
            return 113.0
        return 33.0

    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        state_path = Path(temp) / "state.json"
        solver.save_state(state_path, seed_state)
        fake = FakeClient("http://offline.invalid", solver.ClientConfig(), latency)
        original_sleep = solver.time.sleep
        solver.time.sleep = lambda _seconds: None
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                recovered = solver.recover(
                    "http://offline.invalid",
                    config=solver.ClientConfig(delay=3.0),
                    state_path=state_path,
                    positions=1,
                    verify_samples=4,
                    accept_margin=12.0,
                    charset="abm",
                    rescreen_every=0,
                    watch=True,
                    watch_hours=1.0,
                    client_factory=lambda _url, _config: fake,
                )
        finally:
            solver.time.sleep = original_sleep
        assert recovered == winner
        assert len(spike_calls) == 2
        assert screen_passes[:4] == [1, 2, 3, 4]
        assert len(screen_passes) <= 6
        saved = solver.load_state(state_path, "http://offline.invalid")
        assert "1" not in saved.get("evidence", {})
        assert fake._per_char_calls[winner] >= 4
    print("ACCUMULATED FLICKER: two spikes across three screens promoted and accepted")


def test_drift_detrending_dual_pass() -> None:
    """Anchors remove a linear load drift and dual passes reject a one-off max."""
    charset = "abcdefghijklmnoprstuvxyz"
    winner = "m"
    transient = "x"
    screening_batch_size = len(charset) + len(charset) // solver.ANCHOR_INTERVAL

    def latency(token: str, call: int, char_call: int) -> float:
        phase_call = (call - 1) % screening_batch_size
        baseline = 33.0 + 15.0 * phase_call / (screening_batch_size - 1)
        if token[0] == winner:
            return baseline + 70.0
        if token[0] == transient and char_call == 1:
            return baseline + 85.0
        return baseline

    with tempfile.TemporaryDirectory(dir="/tmp") as temp:
        fake = FakeClient("http://offline.invalid", solver.ClientConfig(), latency)
        recovered = _run_recovery(
            fake,
            charset=charset,
            state_path=Path(temp) / "state.json",
        )

    first_samples: dict[str, float] = {}
    for token, raw_latency in fake.calls:
        char = token[0]
        if char in charset:
            first_samples.setdefault(char, raw_latency)
    naive = max(first_samples, key=first_samples.get)
    assert recovered == winner
    assert naive == transient
    print(
        f"T8 DRIFT: detrended dual-pass selected {recovered!r}; "
        f"naive single-pass raw max would select {naive!r}"
    )


def test_sigma_hygiene() -> None:
    """The robust noise estimate excludes the current top two scores."""
    scores = [(0.0, "a"), (1.0, "b"), (2.0, "c"), (3.0, "d"), (4.0, "e"), (100.0, "m")]
    sigma_hygienic = solver.batch_statistics(scores)[1]
    sigma_with_winner = solver.batch_statistics(scores, exclude_top_k=0)[1]
    assert sigma_with_winner > sigma_hygienic
    assert sigma_hygienic == solver.batch_statistics(scores, exclude_top_k=2)[1]
    print(
        f"T9 SIGMA: excluded-top-2 sigma={sigma_hygienic:.3f} vs "
        f"unfiltered sigma={sigma_with_winner:.3f}"
    )


def main() -> None:
    tests = (
        test_clean_signal,
        test_flicker_signal,
        test_no_signal,
        test_artifact_guard,
        test_sprt,
        test_cadence_controller,
        test_accumulated_flicker_signal,
        test_drift_detrending_dual_pass,
        test_sigma_hygiene,
    )
    for test in tests:
        test()
    print(f"PASS: {len(tests)} offline solver checks")


if __name__ == "__main__":
    main()
