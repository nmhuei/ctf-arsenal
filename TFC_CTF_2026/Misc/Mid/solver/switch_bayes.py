"""Compact Bayesian tracker for the Mid challenge's one-time state switch."""

from dataclasses import dataclass


@dataclass
class _Branch:
    low: int
    high: int
    weight: float


class SwitchBayes:
    """Track ``switch_at`` without enumerating the password space.

    For a fixed switch point, truthful answers only intersect the password
    with an interval; random answers multiply the branch likelihood by 1/2.
    Therefore each of the 196 switch-point hypotheses needs only an interval,
    rather than a posterior array of size ``62**30``.
    """

    def __init__(self, size: int, max_queries: int):
        if size < 2:
            raise ValueError("size must be at least 2")
        if max_queries < 1:
            raise ValueError("max_queries must be positive")
        prior = 1.0 / (max_queries + 1)
        self.size = size
        self.max_queries = max_queries
        self._branches = {
            switch_at: _Branch(0, size - 1, prior)
            for switch_at in range(max_queries + 1)
        }

    def _is_truthful(self, switch_at: int, query_id: int, state: int) -> bool:
        mood = 1 if query_id >= switch_at else 0
        return state == mood

    def choose_state(self, query_id: int) -> int:
        masses = [0.0, 0.0]
        for switch_at, branch in self._branches.items():
            if branch.weight:
                state = 1 if query_id >= switch_at else 0
                masses[state] += branch.weight
        return 0 if masses[0] >= masses[1] else 1

    def choose_guess(self, query_id: int, state: int) -> int:
        """Return a posterior median among branches where this state is true."""
        truthful = [
            branch
            for switch_at, branch in self._branches.items()
            if branch.weight and self._is_truthful(switch_at, query_id, state)
        ]
        if not truthful:
            truthful = [branch for branch in self._branches.values() if branch.weight]

        total = sum(branch.weight for branch in truthful)
        target = total / 2.0
        low, high = 0, self.size - 1
        while low < high:
            guess = (low + high) // 2
            cumulative = 0.0
            for branch in truthful:
                if guess >= branch.high:
                    covered = branch.high - branch.low + 1
                elif guess < branch.low:
                    covered = 0
                else:
                    covered = guess - branch.low + 1
                cumulative += branch.weight * covered / (branch.high - branch.low + 1)
            if cumulative >= target:
                high = guess
            else:
                low = guess + 1
        return low

    def observe(self, query_id: int, state: int, guess: int, response: str) -> None:
        """Update switch and interval hypotheses with one server response."""
        if response not in {"smaller", "larger"}:
            raise ValueError(f"unsupported response: {response!r}")
        for switch_at, branch in self._branches.items():
            if not branch.weight:
                continue
            if not self._is_truthful(switch_at, query_id, state):
                branch.weight *= 0.5
                continue

            old_size = branch.high - branch.low + 1
            if response == "smaller":
                branch.low = max(branch.low, guess + 1)
            else:
                branch.high = min(branch.high, guess - 1)
            new_size = branch.high - branch.low + 1
            if new_size <= 0:
                branch.weight = 0.0
            else:
                branch.weight *= new_size / old_size

        total = sum(branch.weight for branch in self._branches.values())
        if total:
            for branch in self._branches.values():
                branch.weight /= total

    def intervals(self) -> dict[int, tuple[int, int]]:
        return {
            switch_at: (branch.low, branch.high)
            for switch_at, branch in self._branches.items()
            if branch.weight
        }
