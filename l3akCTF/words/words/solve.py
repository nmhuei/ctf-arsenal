#!/usr/bin/env python3
"""
Persistent-learning WordGuess/Wordle solver.

Features
--------
* Standard-library only.
* Exact duplicate-letter feedback handling.
* Persistent empirical answer frequency across connections.
* Per-slot learning: word 17/100 can learn a different distribution from word 3/100.
* Structural learning from solved answers: letter position and positional bigrams.
* Bayesian-style smoothing so early history does not dominate.
* Fast weighted-frequency mode for huge candidate sets.
* Weighted entropy/minimax for medium and small candidate sets.
* Exact expected-turn dynamic programming for tiny endgames.
* Atomic history writes, duplicate-event protection, reconnect loop, rich logs.

The script assumes every accepted word is exactly five ASCII letters and that
words.txt contains one word per line.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import socket
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

DEFAULT_HOST = "5.161.227.224"
DEFAULT_PORT = 1337
DEFAULT_TOKEN = (
    "803bdb1f-117d-439a-941a-d7ddba7a4df4:"
    "93c999bed4ceeec484f9750084e92d4337c8c6bd9c1e959eeeae6c9593f5919e"
)
DEFAULT_WORDLIST = "words.txt"
DEFAULT_HISTORY = "wordguest_history.json"
DEFAULT_SOLVED_LIST = "solved_words.txt"
DEFAULT_SESSION_LOG = "wordguest_sessions.jsonl"

WORD_LEN = 5
GRAY, YELLOW, GREEN = 0, 1, 2
EMOJI_VALUE = {"⬜": GRAY, "⬛": GRAY, "🟨": YELLOW, "🟩": GREEN}
VALUE_TEXT = {GRAY: "B", YELLOW: "Y", GREEN: "G"}
WORD_RE = re.compile(r"^[a-z]{5}$")
PROMPT_RE = re.compile(
    r"round\s+(\d+),\s*word\s+(\d+)/(\d+),\s*guess\s+(\d+),\s*"
    r"((?:[⬜⬛🟨🟩]\s*){5})\s*>",
    re.I,
)
# Flag responses can replace the five color cells; they are saved and play continues.
# Keep a separate state-only parser so these lines are still understood.
STATE_RE = re.compile(
    r"round\s+(\d+),\s*word\s+(\d+)/(\d+),\s*guess\s+(\d+),",
    re.I,
)
FLAG_RE = re.compile(r"\bL3AK\{[^{}\r\n]+\}", re.I)


def log(message: str = "") -> None:
    print(message, flush=True)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def pattern_to_text(code: int) -> str:
    out: List[str] = []
    for _ in range(WORD_LEN):
        out.append(VALUE_TEXT[code % 3])
        code //= 3
    return "".join(out)


def text_to_pattern(text: str) -> int:
    code = 0
    multiplier = 1
    values = {"B": GRAY, "Y": YELLOW, "G": GREEN}
    for char in text:
        code += values[char] * multiplier
        multiplier *= 3
    return code


ALL_GREEN = text_to_pattern("GGGGG")


@lru_cache(maxsize=2_000_000)
def feedback_code(guess: str, answer: str) -> int:
    """Return Wordle feedback in base 3, correctly handling duplicates."""
    result = [GRAY] * WORD_LEN
    remaining = [0] * 26

    for index in range(WORD_LEN):
        if guess[index] == answer[index]:
            result[index] = GREEN
        else:
            remaining[ord(answer[index]) - 97] += 1

    for index in range(WORD_LEN):
        if result[index] == GREEN:
            continue
        letter = ord(guess[index]) - 97
        if remaining[letter] > 0:
            result[index] = YELLOW
            remaining[letter] -= 1

    code = 0
    multiplier = 1
    for value in result:
        code += value * multiplier
        multiplier *= 3
    return code


@dataclass(frozen=True)
class PromptState:
    round_id: int
    word_id: int
    total_words: int
    guess_no: int


def parse_last_prompt(text: str) -> Tuple[Optional[PromptState], Optional[int]]:
    clean = text.replace("\ufe0f", "")
    matches = list(PROMPT_RE.finditer(clean))
    if matches:
        match = matches[-1]
        state = PromptState(
            round_id=int(match.group(1)),
            word_id=int(match.group(2)),
            total_words=int(match.group(3)),
            guess_no=int(match.group(4)),
        )

        colors = [EMOJI_VALUE[ch] for ch in match.group(5) if ch in EMOJI_VALUE]
        if len(colors) != WORD_LEN:
            return state, None

        code = 0
        multiplier = 1
        for value in colors:
            code += value * multiplier
            multiplier *= 3
        return state, code

    # A terminal line may look like:
    # round 220, word 2/100, guess 4, L3AK{...} >
    # It has valid state information but no color pattern.
    state_matches = list(STATE_RE.finditer(clean))
    if not state_matches:
        return None, None

    match = state_matches[-1]
    return (
        PromptState(
            round_id=int(match.group(1)),
            word_id=int(match.group(2)),
            total_words=int(match.group(3)),
            guess_no=int(match.group(4)),
        ),
        None,
    )


def extract_flag(text: str) -> Optional[str]:
    match = FLAG_RE.search(text)
    return match.group(0) if match else None


# Global precomputed letter sets for all words (populated by load_wordlist)
_WORD_LETTER_SETS: Dict[str, frozenset] = {}


def load_wordlist(path: str) -> List[str]:
    seen: Set[str] = set()
    words: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            word = line.strip().lower()
            if WORD_RE.fullmatch(word) and word not in seen:
                seen.add(word)
                words.append(word)
    # Precompute letter sets for fast diff probe scoring
    for w in words:
        _WORD_LETTER_SETS[w] = frozenset(w)
    return words


class PersistentLearner:
    """Stores solved answers and builds a smoothed empirical prior."""

    VERSION = 3

    def __init__(self, history_path: str, solved_list_path: str, server_id: str):
        self.history_path = Path(history_path)
        self.solved_list_path = Path(solved_list_path)
        self.server_id = server_id

        self.events: Dict[str, str] = {}
        self.global_counts: Counter[str] = Counter()
        self.slot_counts: Dict[int, Counter[str]] = defaultdict(Counter)

        self.position_counts: List[Counter[str]] = [Counter() for _ in range(WORD_LEN)]
        self.bigram_counts: List[Counter[str]] = [Counter() for _ in range(WORD_LEN - 1)]
        self.presence_counts: Counter[str] = Counter()
        self.total_solved = 0

        self.load()

    def _event_key(self, round_id: int, word_id: int) -> str:
        return f"{self.server_id}|{round_id}:{word_id}"

    def load(self) -> None:
        migrated = False

        if self.history_path.exists():
            try:
                data = json.loads(self.history_path.read_text(encoding="utf-8"))
                raw_events = data.get("events", {})

                # Version-1/2 migration: events may be keyed only by round:word.
                for raw_key, raw_word in raw_events.items():
                    word = str(raw_word).lower()
                    if not WORD_RE.fullmatch(word):
                        continue
                    key = str(raw_key)
                    if "|" not in key:
                        key = f"{self.server_id}|{key}"
                    self.events[key] = word

                # Some older files stored only aggregate counts. Preserve them
                # as global-only pseudo-events instead of silently losing data.
                if not self.events:
                    raw_counts = data.get("global_counts", data.get("counts", {}))
                    serial = 0
                    for raw_word, raw_count in raw_counts.items():
                        word = str(raw_word).lower()
                        try:
                            count = int(raw_count)
                        except (TypeError, ValueError):
                            continue
                        if not WORD_RE.fullmatch(word) or count <= 0:
                            continue
                        for _ in range(count):
                            serial += 1
                            self.events[f"legacy|global:{serial}"] = word
                    migrated = bool(self.events)
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
                log(f"[WARN] Cannot load history {self.history_path}: {error}")

        # Also import an existing solved_words.txt when JSON history is absent.
        if not self.events and self.solved_list_path.exists():
            try:
                serial = 0
                for line in self.solved_list_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines():
                    word = line.strip().lower()
                    if WORD_RE.fullmatch(word):
                        serial += 1
                        self.events[f"legacy|global:{serial}"] = word
                migrated = bool(self.events)
            except OSError as error:
                log(f"[WARN] Cannot import {self.solved_list_path}: {error}")

        # Events are the canonical source; rebuild every derived counter.
        self._rebuild()
        if self.total_solved:
            log(
                f"[LEARN] Loaded {self.total_solved} solved events, "
                f"{len(self.global_counts)} unique answers"
            )
            if migrated:
                log("[LEARN] Migrated legacy learning data")
                self.save()
            top = ", ".join(
                f"{word}:{count}" for word, count in self.global_counts.most_common(10)
            )
            log(f"[LEARN] Top answers: {top}")

    def _rebuild(self) -> None:
        self.global_counts = Counter()
        self.slot_counts = defaultdict(Counter)

        for key, word in self.events.items():
            self.global_counts[word] += 1

            # Only real events from this server contribute to per-slot
            # statistics. Legacy aggregate imports remain global-only.
            if not key.startswith(f"{self.server_id}|"):
                continue
            try:
                slot = int(key.rsplit(":", 1)[1])
            except (IndexError, ValueError):
                continue
            self.slot_counts[slot][word] += 1

        self.total_solved = sum(self.global_counts.values())
        self.position_counts = [Counter() for _ in range(WORD_LEN)]
        self.bigram_counts = [Counter() for _ in range(WORD_LEN - 1)]
        self.presence_counts = Counter()

        for word, count in self.global_counts.items():
            for index, letter in enumerate(word):
                self.position_counts[index][letter] += count
            for index in range(WORD_LEN - 1):
                self.bigram_counts[index][word[index : index + 2]] += count
            for letter in set(word):
                self.presence_counts[letter] += count

    def known_words(self) -> List[str]:
        return list(self.global_counts)

    def record(self, state: PromptState, word: str, reason: str) -> bool:
        word = word.lower()
        if not WORD_RE.fullmatch(word):
            return False

        key = self._event_key(state.round_id, state.word_id)
        previous = self.events.get(key)
        if previous == word:
            return False

        self.events[key] = word
        self._rebuild()
        self.save()
        log(
            f"[LEARN] + {word} at round={state.round_id}, slot={state.word_id} "
            f"({reason}); global={self.global_counts[word]}, "
            f"slot={self.slot_counts[state.word_id][word]}, total={self.total_solved}"
        )
        return True

    def save(self) -> None:
        payload = {
            "version": self.VERSION,
            "server": self.server_id,
            "events": dict(sorted(self.events.items())),
            "global_counts": dict(sorted(self.global_counts.items())),
            "slot_counts": {
                str(slot): dict(sorted(counter.items()))
                for slot, counter in sorted(self.slot_counts.items())
            },
            "updated_at": int(time.time()),
        }

        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.history_path.with_suffix(self.history_path.suffix + ".tmp")
            temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temp, self.history_path)

            self.solved_list_path.parent.mkdir(parents=True, exist_ok=True)
            lines: List[str] = []
            for word, count in self.global_counts.most_common():
                lines.extend([word] * count)
            self.solved_list_path.write_text(
                "".join(f"{word}\n" for word in lines), encoding="utf-8"
            )
        except OSError as error:
            log(f"[WARN] Cannot save history: {error}")

    def weight(
        self,
        word: str,
        slot: int,
        solved_in_round: Set[str],
        global_strength: float,
        slot_strength: float,
        structure_strength: float,
        repeat_penalty: float,
    ) -> float:
        """Return an unnormalized posterior prior for one candidate answer."""
        global_count = self.global_counts.get(word, 0)
        slot_count = self.slot_counts.get(slot, Counter()).get(word, 0)

        # Exact empirical frequency: the core requested learning behavior.
        exact_factor = 1.0 + global_strength * global_count

        # Slot-specific frequency. Reliability prevents one observation from
        # becoming overwhelmingly dominant.
        slot_total = sum(self.slot_counts.get(slot, Counter()).values())
        slot_reliability = slot_total / (slot_total + 5.0)
        slot_factor = 1.0 + slot_strength * slot_reliability * slot_count

        # Learn the shape of likely answers for words never seen exactly.
        # The model fades in gradually as solved data accumulates.
        structure_reliability = self.total_solved / (self.total_solved + 80.0)
        structural_log_ratio = 0.0
        if self.total_solved > 0 and structure_strength > 0:
            alpha_letter = 1.0
            alpha_bigram = 0.25

            for index, letter in enumerate(word):
                observed = self.position_counts[index][letter]
                probability = (observed + alpha_letter) / (
                    self.total_solved + 26.0 * alpha_letter
                )
                structural_log_ratio += math.log(probability * 26.0)

            for index in range(WORD_LEN - 1):
                pair = word[index : index + 2]
                observed = self.bigram_counts[index][pair]
                probability = (observed + alpha_bigram) / (
                    self.total_solved + 676.0 * alpha_bigram
                )
                structural_log_ratio += 0.35 * math.log(probability * 676.0)

        structural_log_ratio *= structure_strength * structure_reliability
        structural_factor = math.exp(clamp(structural_log_ratio, -4.0, 4.0))

        weight = exact_factor * slot_factor * structural_factor
        if word in solved_in_round:
            weight *= repeat_penalty
        return max(weight, 1e-12)


class SessionLogger:
    def __init__(self, path: str):
        self.path = Path(path)

    def write(self, event: dict) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = dict(event)
            payload["timestamp"] = int(time.time())
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except OSError as error:
            log(f"[WARN] Cannot write session log: {error}")


def filter_candidates(candidates: Sequence[str], guess: str, observed: int) -> List[str]:
    return [word for word in candidates if feedback_code(guess, word) == observed]


def make_weight_map(
    candidates: Sequence[str],
    learner: PersistentLearner,
    slot: int,
    solved_in_round: Set[str],
    args: argparse.Namespace,
) -> Dict[str, float]:
    return {
        word: learner.weight(
            word=word,
            slot=slot,
            solved_in_round=solved_in_round,
            global_strength=args.global_strength,
            slot_strength=args.slot_strength,
            structure_strength=args.structure_strength,
            repeat_penalty=args.repeat_penalty,
        )
        for word in candidates
    }


def build_weighted_frequency(
    candidates: Sequence[str], weight_map: Dict[str, float]
) -> Tuple[List[defaultdict], defaultdict]:
    positional = [defaultdict(float) for _ in range(WORD_LEN)]
    global_frequency = defaultdict(float)

    for answer in candidates:
        weight = weight_map[answer]
        used: Set[str] = set()
        for index, letter in enumerate(answer):
            positional[index][letter] += weight
            if letter not in used:
                global_frequency[letter] += weight
                used.add(letter)
    return positional, global_frequency


def frequency_score(
    word: str,
    positional: Sequence[defaultdict],
    global_frequency: defaultdict,
) -> float:
    score = 0.0
    used: Set[str] = set()
    scale = max(global_frequency.values(), default=1.0)
    for index, letter in enumerate(word):
        score += 3.0 * positional[index][letter]
        if letter not in used:
            score += 2.0 * global_frequency[letter]
            used.add(letter)
        else:
            score -= 0.20 * scale
    return score


def top_frequency_words(
    pool: Sequence[str],
    candidates: Sequence[str],
    weight_map: Dict[str, float],
    limit: int,
    excluded: Set[str],
) -> List[str]:
    positional, global_frequency = build_weighted_frequency(candidates, weight_map)
    scored = [
        (frequency_score(word, positional, global_frequency), word)
        for word in pool
        if word not in excluded
    ]
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [word for _, word in scored[:limit]]


def evaluate_guess(
    guess: str,
    candidates: Sequence[str],
    weight_map: Dict[str, float],
) -> dict:
    bucket_mass: Dict[int, float] = defaultdict(float)
    bucket_count: Dict[int, int] = defaultdict(int)
    total_mass = sum(weight_map[word] for word in candidates)

    for answer in candidates:
        pattern = feedback_code(guess, answer)
        bucket_mass[pattern] += weight_map[answer]
        bucket_count[pattern] += 1

    entropy = 0.0
    expected_count = 0.0
    expected_mass = 0.0
    worst_count = 0
    worst_mass = 0.0

    for pattern, mass in bucket_mass.items():
        probability = mass / total_mass
        count = bucket_count[pattern]
        entropy -= probability * math.log2(probability)
        expected_count += probability * count
        expected_mass += probability * probability
        worst_count = max(worst_count, count)
        worst_mass = max(worst_mass, probability)

    solve_probability = (
        weight_map.get(guess, 0.0) / total_mass if guess in weight_map else 0.0
    )
    return {
        "entropy": entropy,
        "expected_count": expected_count,
        "expected_mass": expected_mass,
        "worst_count": worst_count,
        "worst_mass": worst_mass,
        "solve_probability": solve_probability,
        "buckets": len(bucket_mass),
    }


def choose_entropy_guess(
    probes: Sequence[str],
    candidates: Sequence[str],
    weight_map: Dict[str, float],
    guess_no: int,
) -> Tuple[str, dict]:
    best_word: Optional[str] = None
    best_stats: Optional[dict] = None
    best_key: Optional[tuple] = None
    tight_budget = guess_no >= 4

    for guess in probes:
        stats = evaluate_guess(guess, candidates, weight_map)
        in_candidates = guess in weight_map

        if tight_budget:
            key = (
                stats["worst_count"],
                stats["expected_count"],
                stats["expected_mass"],
                -stats["solve_probability"],
                -stats["entropy"],
                not in_candidates,
            )
        else:
            key = (
                stats["expected_mass"],
                stats["expected_count"],
                stats["worst_count"],
                -stats["entropy"],
                -stats["solve_probability"],
                not in_candidates,
            )

        if best_key is None or key < best_key:
            best_key = key
            best_word = guess
            best_stats = stats

    assert best_word is not None and best_stats is not None
    return best_word, best_stats


def _precompute_diff_probes(
    all_words: Sequence[str],
    candidates: Sequence[str],
    limit: int = 30,
) -> List[str]:
    """Pre-compute the best differentiating probe words once at top level."""
    diff_letters: Set[str] = set()
    for i in range(WORD_LEN):
        chars = {w[i] for w in candidates}
        if len(chars) > 1:
            diff_letters.update(chars)
    if len(diff_letters) <= 1:
        return []
    diff_fs = frozenset(diff_letters)
    cand_set = set(candidates)
    # Use precomputed letter sets for O(1) intersection size
    scored = [(len(_WORD_LETTER_SETS.get(w, frozenset(w)) & diff_fs), w)
              for w in all_words if w not in cand_set]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [w for _, w in scored[:limit]]


def exact_endgame_guess(
    candidates: Sequence[str],
    weight_map: Dict[str, float],
    all_words: Optional[Sequence[str]] = None,
) -> Tuple[str, float, int]:
    """Exact expected-turn DP, using candidates and letter-differentiating probes."""
    ordered = tuple(sorted(candidates))
    memo: Dict[Tuple[str, ...], float] = {}
    choice: Dict[Tuple[str, ...], str] = {}

    # Pre-compute diff probes ONCE for the top-level candidate set
    top_diff_probes: List[str] = []
    if all_words and len(ordered) > 2:
        top_diff_probes = _precompute_diff_probes(all_words, candidates, limit=80)

    def solve_cost(state: Tuple[str, ...]) -> float:
        if len(state) == 1:
            choice[state] = state[0]
            return 1.0
        if state in memo:
            return memo[state]

        total_weight = sum(weight_map[word] for word in state)
        best_cost = float("inf")
        best_guess = state[0]

        # Use candidates + pre-computed diff probes (no re-sorting)
        probes: List[str] = list(state)
        state_set = set(state)
        for p in top_diff_probes:
            if p not in state_set:
                probes.append(p)

        for guess in probes:
            buckets: Dict[int, List[str]] = defaultdict(list)
            for answer in state:
                pattern = feedback_code(guess, answer)
                if pattern != ALL_GREEN:
                    buckets[pattern].append(answer)

            # A guess that leaves the whole non-solved state unchanged can recurse forever.
            if any(len(bucket) == len(state) for bucket in buckets.values()):
                continue

            cost = 1.0
            for bucket in buckets.values():
                bucket_state = tuple(sorted(bucket))
                bucket_weight = sum(weight_map[word] for word in bucket_state)
                cost += (bucket_weight / total_weight) * solve_cost(bucket_state)

            if cost < best_cost - 1e-12:
                best_cost = cost
                best_guess = guess
            elif abs(cost - best_cost) <= 1e-12:
                if weight_map.get(guess, 0.0) > weight_map.get(best_guess, 0.0):
                    best_guess = guess

        memo[state] = best_cost
        choice[state] = best_guess
        return best_cost

    expected = solve_cost(ordered)
    return choice[ordered], expected, len(memo)


def build_probe_pool(
    all_words: Sequence[str],
    candidates: Sequence[str],
    weight_map: Dict[str, float],
    learner: PersistentLearner,
    limit: int,
    guessed: Set[str],
) -> List[str]:
    candidate_top = top_frequency_words(
        candidates,
        candidates,
        weight_map,
        max(1, min(limit, len(candidates))),
        guessed,
    )
    global_top = top_frequency_words(
        all_words,
        candidates,
        weight_map,
        max(1, min(limit, len(all_words))),
        guessed,
    )

    diff_probes: List[str] = []
    if 1 < len(candidates) <= 300:
        diff_probes = _precompute_diff_probes(all_words, candidates, limit=40)

    all_word_set = set(all_words)
    learned_top = [
        word
        for word, _ in learner.global_counts.most_common(200)
        if word in all_word_set and word not in guessed
    ]

    probes: List[str] = []
    seen: Set[str] = set()
    for word in candidate_top + diff_probes + learned_top + global_top:
        if word not in seen and word not in guessed:
            probes.append(word)
            seen.add(word)
    return probes


def choose_guess(
    candidates: Sequence[str],
    all_words: Sequence[str],
    state: PromptState,
    learner: PersistentLearner,
    solved_in_round: Set[str],
    guessed: Set[str],
    args: argparse.Namespace,
) -> str:
    count = len(candidates)
    if count == 0:
        raise ValueError("choose_guess called with no candidates")

    weight_map = make_weight_map(
        candidates, learner, state.word_id, solved_in_round, args
    )

    if count <= 2:
        log(f"[MODE] {count} candidate(s)")
        best_cand = max(candidates, key=lambda w: weight_map[w])
        return best_cand

    if count <= args.exact_threshold:
        log("[MODE] exact expected-turn endgame")
        word, expected, states = exact_endgame_guess(candidates, weight_map, all_words)
        log(
            f"[EXACT] best={word}, expected_turns={expected:.4f}, states={states}, "
            f"global_seen={learner.global_counts.get(word, 0)}, "
            f"slot_seen={learner.slot_counts[state.word_id].get(word, 0)}"
        )
        return word

    if count > args.frequency_threshold:
        log("[MODE] huge set -> learned weighted frequency")
        slot_hist = learner.slot_counts.get(state.word_id, Counter())
        available_slot = [w for w, _ in slot_hist.most_common() if w in candidates and w not in guessed and w not in solved_in_round]
        if available_slot:
            best_slot_word = available_slot[0]
            log(f"[SLOT-PRIOR] Opening guess for slot {state.word_id}: {best_slot_word} (seen {slot_hist[best_slot_word]}x)")
            return best_slot_word

        positional, global_frequency = build_weighted_frequency(candidates, weight_map)
        available = [word for word in candidates if word not in guessed]
        if not available:
            available = list(candidates)
        word = max(
            available,
            key=lambda item: (
                frequency_score(item, positional, global_frequency),
                weight_map[item],
            ),
        )
        log(
            f"[FREQ] best={word}, global_seen={learner.global_counts.get(word, 0)}, "
            f"slot_seen={learner.slot_counts[state.word_id].get(word, 0)}, "
            f"prior={weight_map[word]:.4f}"
        )
        return word

    local_guess_no = len(guessed) + 1
    if local_guess_no == 2 and count > 150:
        for opener_word in ("colin", "pudic", "ymolt", "shout", "blimp"):
            if opener_word not in guessed:
                log(f"[OPENER-2] 2-word opener combo: {opener_word} (local_guess=2, candidates={count})")
                return opener_word

    if count > 1000:
        probe_limit = 250
        mode = "large set -> sampled weighted entropy"
    elif count > 300:
        probe_limit = 450
        mode = "medium set -> weighted entropy"
    elif count > 60:
        probe_limit = 900
        mode = "small set -> strong entropy/minimax"
    else:
        probe_limit = 1800
        mode = "endgame -> broad entropy/minimax"

    log(f"[MODE] {mode}")
    probes = build_probe_pool(
        all_words=all_words,
        candidates=candidates,
        weight_map=weight_map,
        learner=learner,
        limit=probe_limit,
        guessed=guessed,
    )
    if not probes:
        probes = [word for word in candidates if word not in guessed] or list(candidates)

    log(f"[SEARCH] {len(probes)} probes x {count} candidates")
    word, stats = choose_entropy_guess(
        probes=probes,
        candidates=candidates,
        weight_map=weight_map,
        guess_no=state.guess_no,
    )
    log(
        f"[INFO] best={word}, entropy={stats['entropy']:.3f}, "
        f"expected={stats['expected_count']:.3f}, worst={stats['worst_count']}, "
        f"solve_p={stats['solve_probability']:.2%}, candidate={word in weight_map}, "
        f"global_seen={learner.global_counts.get(word, 0)}, "
        f"slot_seen={learner.slot_counts[state.word_id].get(word, 0)}"
    )
    return word


def soft_recovery_guess(
    all_words: Sequence[str],
    constraints: Sequence[Tuple[str, int]],
    guessed: Set[str],
    learner: PersistentLearner,
    state: PromptState,
    solved_in_round: Set[str],
    args: argparse.Namespace,
) -> str:
    """Recover gracefully when the wordlist/feedback produces zero candidates."""
    best_word: Optional[str] = None
    best_key: Optional[tuple] = None

    for word in all_words:
        if word in guessed:
            continue
        matched = sum(
            1 for old_guess, code in constraints if feedback_code(old_guess, word) == code
        )
        prior = learner.weight(
            word,
            state.word_id,
            solved_in_round,
            args.global_strength,
            args.slot_strength,
            args.structure_strength,
            args.repeat_penalty,
        )
        key = (matched, prior)
        if best_key is None or key > best_key:
            best_key = key
            best_word = word

    if best_word is None:
        best_word = all_words[0]
    log(f"[RECOVER] soft-constraint guess={best_word}, matched={best_key[0] if best_key else 0}")
    return best_word


class ServerClosed(ConnectionError):
    def __init__(self, text: str = ""):
        super().__init__("server closed the connection")
        self.text = text


def recv_until_prompt(sock: socket.socket) -> str:
    data = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            text = data.decode("utf-8", errors="ignore")
            if text:
                print(text, end="", flush=True)
            raise ServerClosed(text)
        data.extend(chunk)
        text = data.decode("utf-8", errors="ignore")
        if ">" in text:
            print(text, end="", flush=True)
            return text


def send_line(sock: socket.socket, value: str, secret: bool = False) -> None:
    shown = "<team token>" if secret else value
    log(f"[SEND] {shown}")
    sock.sendall((value + "\n").encode())


def append_history_words(words: List[str], learner: PersistentLearner) -> List[str]:
    seen = set(words)
    added = 0
    for word in learner.known_words():
        if word not in seen:
            words.append(word)
            seen.add(word)
            added += 1
    if added:
        log(f"[LEARN] Added {added} historical answers missing from words.txt")
    return words


def play_connection(
    args: argparse.Namespace,
    learner: PersistentLearner,
    session_log: SessionLogger,
    all_words: List[str],
) -> None:
    log(f"[NET] Connecting to {args.host}:{args.port}")
    sock = socket.create_connection((args.host, args.port), timeout=args.timeout)
    sock.settimeout(args.timeout)

    current_state: Optional[PromptState] = None
    candidates: List[str] = list(all_words)
    constraints: List[Tuple[str, int]] = []
    guessed: Set[str] = set()
    solved_in_round: Set[str] = set()

    pending_guess: Optional[str] = None
    pending_state: Optional[PromptState] = None

    try:
        while True:
            try:
                text = recv_until_prompt(sock)
            except ServerClosed as closed:
                terminal = closed.text.lower()
                success_markers = ("flag", "l3ak{", "congrat", "completed", "success")
                if (
                    pending_guess is not None
                    and pending_state is not None
                    and any(marker in terminal for marker in success_markers)
                ):
                    learner.record(
                        pending_state, pending_guess, reason="terminal success"
                    )
                    solved_in_round.add(pending_guess)
                    session_log.write(
                        {
                            "type": "solved",
                            "round": pending_state.round_id,
                            "word_id": pending_state.word_id,
                            "answer": pending_guess,
                            "reason": "terminal success",
                        }
                    )
                raise

            lower = text.lower()

            if "team token" in lower:
                send_line(sock, args.token, secret=True)
                continue

            # A correct answer may replace the five color cells with a flag while
            # leaving the socket open. That flag is an intermediate reward, not a
            # terminal response: save the solved word and immediately start the
            # next word on the same connection.
            flag = extract_flag(text)
            if flag is not None:
                state, _ = parse_last_prompt(text)
                solved_state = pending_state or state
                solved_answer = pending_guess

                if solved_answer is not None and solved_state is not None:
                    learner.record(solved_state, solved_answer, reason="flag response")
                    solved_in_round.add(solved_answer)
                    session_log.write(
                        {
                            "type": "solved",
                            "round": solved_state.round_id,
                            "word_id": solved_state.word_id,
                            "answer": solved_answer,
                            "reason": "flag response",
                            "flag": flag,
                        }
                    )

                session_log.write(
                    {
                        "type": "flag",
                        "round": state.round_id if state else None,
                        "word_id": state.word_id if state else None,
                        "flag": flag,
                    }
                )
                log(f"[FLAG] {flag}")
                log("[SUCCESS] Correct word saved; continuing on the same connection")

                pending_guess = None
                pending_state = None

                # Prefer the state printed beside the flag. It identifies the next word.
                # Fall back to pending_state when necessary.
                completed_state = state or solved_state
                if completed_state is None:
                    log("[WARN] Flag found without state; waiting for the next prompt")
                    continue

                if solved_state and solved_state.word_id >= solved_state.total_words:
                    log(
                        f"[COMPLETE] Finished {solved_state.total_words}/"
                        f"{solved_state.total_words} words in round "
                        f"{solved_state.round_id}"
                    )
                    return

                # The flag line parsed by parse_last_prompt(text) contains state,
                # where state.word_id is ALREADY the next word to solve.
                if state is not None and solved_state is not None:
                    next_word_id = max(state.word_id, solved_state.word_id + 1)
                elif state is not None:
                    next_word_id = state.word_id
                elif solved_state is not None:
                    next_word_id = solved_state.word_id + 1
                else:
                    next_word_id = completed_state.word_id

                next_state = PromptState(
                    round_id=completed_state.round_id,
                    word_id=next_word_id,
                    total_words=completed_state.total_words,
                    guess_no=0,
                )
                current_state = next_state
                candidates = list(all_words)
                constraints = []
                guessed = set()

                log(
                    f"[NEW] round={next_state.round_id}, "
                    f"word={next_state.word_id}/{next_state.total_words}; "
                    f"candidates={len(candidates)} (advanced after flag)"
                )

                next_guess = choose_guess(
                    candidates=candidates,
                    all_words=all_words,
                    state=next_state,
                    learner=learner,
                    solved_in_round=solved_in_round,
                    guessed=guessed,
                    args=args,
                )
                guessed.add(next_guess)
                send_line(sock, next_guess)
                pending_guess = next_guess
                pending_state = next_state
                time.sleep(args.send_delay)
                continue

            state, observed = parse_last_prompt(text)
            if state is None:
                log("[WARN] Could not parse game prompt")
                continue

            if (
                current_state is not None
                and state.round_id == current_state.round_id
                and state.word_id < current_state.word_id
            ):
                continue

            log(
                f"\n[STATE] round={state.round_id}, word={state.word_id}/{state.total_words}, "
                f"guess={state.guess_no}, feedback="
                f"{pattern_to_text(observed) if observed is not None else None}"
            )

            # The prompt belongs to a new word. The immediately preceding guess
            # therefore solved the previous word even if the server skipped a
            # visible GGGGG prompt.
            if pending_guess is not None and pending_state is not None:
                same_word = (
                    state.round_id == pending_state.round_id
                    and state.word_id == pending_state.word_id
                )

                if not same_word:
                    learner.record(pending_state, pending_guess, reason="server advanced")
                    solved_in_round.add(pending_guess)
                    session_log.write(
                        {
                            "type": "solved",
                            "round": pending_state.round_id,
                            "word_id": pending_state.word_id,
                            "answer": pending_guess,
                            "reason": "server advanced",
                        }
                    )
                    pending_guess = None
                    pending_state = None

            is_new_word = (
                current_state is None
                or state.round_id != current_state.round_id
                or state.word_id != current_state.word_id
            )

            if is_new_word:
                if current_state is None or state.round_id != current_state.round_id:
                    solved_in_round = set()
                current_state = state
                candidates = list(all_words)
                constraints = []
                guessed = set()
                log(
                    f"[NEW] round={state.round_id}, word={state.word_id}/{state.total_words}; "
                    f"candidates={len(candidates)}"
                )

            # Apply the observed feedback to the pending guess only when both
            # refer to the same word. Ignore the synthetic BBBBB at guess 0.
            if (
                pending_guess is not None
                and pending_state is not None
                and state.round_id == pending_state.round_id
                and state.word_id == pending_state.word_id
                and observed is not None
                and state.guess_no > 0
            ):
                if observed == ALL_GREEN:
                    learner.record(pending_state, pending_guess, reason="all green")
                    solved_in_round.add(pending_guess)
                    session_log.write(
                        {
                            "type": "solved",
                            "round": pending_state.round_id,
                            "word_id": pending_state.word_id,
                            "answer": pending_guess,
                            "reason": "all green",
                        }
                    )
                    pending_guess = None
                    pending_state = None
                    # Normally the server advances automatically. Read again.
                    continue

                before = len(candidates)
                constraints.append((pending_guess, observed))
                candidates = filter_candidates(candidates, pending_guess, observed)
                log(
                    f"[FILTER] {pending_guess} / {pattern_to_text(observed)}: "
                    f"{before} -> {len(candidates)}"
                )
                session_log.write(
                    {
                        "type": "feedback",
                        "round": state.round_id,
                        "word_id": state.word_id,
                        "guess_no": state.guess_no,
                        "guess": pending_guess,
                        "feedback": pattern_to_text(observed),
                        "before": before,
                        "after": len(candidates),
                    }
                )
                pending_guess = None
                pending_state = None

            if candidates:
                if len(candidates) <= 30:
                    ranked = sorted(
                        candidates,
                        key=lambda word: learner.weight(
                            word,
                            state.word_id,
                            solved_in_round,
                            args.global_strength,
                            args.slot_strength,
                            args.structure_strength,
                            args.repeat_penalty,
                        ),
                        reverse=True,
                    )
                    log(f"[CANDIDATES] {ranked}")

                next_guess = choose_guess(
                    candidates=candidates,
                    all_words=all_words,
                    state=state,
                    learner=learner,
                    solved_in_round=solved_in_round,
                    guessed=guessed,
                    args=args,
                )
            else:
                log("[WARN] No exact candidate remains; entering soft recovery")
                next_guess = soft_recovery_guess(
                    all_words=all_words,
                    constraints=constraints,
                    guessed=guessed,
                    learner=learner,
                    state=state,
                    solved_in_round=solved_in_round,
                    args=args,
                )

            guessed.add(next_guess)
            send_line(sock, next_guess)
            pending_guess = next_guess
            pending_state = state
            time.sleep(args.send_delay)

    finally:
        try:
            sock.close()
        except OSError:
            pass


def print_stats(learner: PersistentLearner) -> None:
    log(f"Solved events: {learner.total_solved}")
    log(f"Unique answers: {len(learner.global_counts)}")
    log("Top global answers:")
    for word, count in learner.global_counts.most_common(30):
        log(f"  {word}: {count}")

    if learner.slot_counts:
        log("Most learned slots:")
        slots = sorted(
            learner.slot_counts.items(),
            key=lambda item: sum(item[1].values()),
            reverse=True,
        )[:15]
        for slot, counts in slots:
            top = ", ".join(f"{w}:{c}" for w, c in counts.most_common(5))
            log(f"  slot {slot}: n={sum(counts.values())}; {top}")


def self_test() -> None:
    tests = [
        ("abcde", "abcde", "GGGGG"),
        ("abcde", "xxxxx", "BBBBB"),
        ("abcde", "eabcd", "YYYYY"),
        ("aabbb", "aaccc", "GGBBB"),
        ("aabbb", "ccaaa", "YYBBB"),
        ("apple", "allee", "GBBYG"),
        ("eerie", "erase", "GBYBG"),
    ]
    for guess, answer, expected in tests:
        actual = pattern_to_text(feedback_code(guess, answer))
        if actual != expected:
            raise AssertionError(
                f"feedback test failed: {guess=} {answer=} {actual=} {expected=}"
            )

    sample = "round 201, word 1/100, guess 4, ⬜️⬜️🟩⬜️🟨 >"
    state, code = parse_last_prompt(sample)
    assert state == PromptState(201, 1, 100, 4)
    assert pattern_to_text(code) == "BBGBY"

    terminal = (
        "round 220, word 2/100, guess 4, "
        "L3AK{w0rdl3:test-token:220:4:1:deadbeef} >"
    )
    state, code = parse_last_prompt(terminal)
    assert state == PromptState(220, 2, 100, 4)
    assert code is None
    assert extract_flag(terminal) == "L3AK{w0rdl3:test-token:220:4:1:deadbeef}"

    with tempfile.TemporaryDirectory() as directory:
        history = str(Path(directory) / "history.json")
        solved = str(Path(directory) / "solved.txt")
        learner = PersistentLearner(history, solved, "test:1")
        s1 = PromptState(1, 7, 100, 3)
        assert learner.record(s1, "crane", "test")
        assert not learner.record(s1, "crane", "duplicate")
        assert learner.global_counts["crane"] == 1
        assert learner.slot_counts[7]["crane"] == 1

        learner2 = PersistentLearner(history, solved, "test:1")
        assert learner2.global_counts["crane"] == 1
        assert learner2.slot_counts[7]["crane"] == 1
        assert learner2.weight("crane", 7, set(), 1.25, 3.0, 0.0, 0.35) > learner2.weight(
            "slate", 7, set(), 1.25, 3.0, 0.0, 0.35
        )

        words = ["crane", "slate", "trace", "cigar", "arose"]
        weights = {word: 1.0 for word in words}
        chosen, expected_turns, _ = exact_endgame_guess(words[:5], weights)
        assert chosen in words
        assert expected_turns >= 1.0

    log("[SELF-TEST] All tests passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Persistent-learning WordGuess solver"
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--token", default=DEFAULT_TOKEN)
    parser.add_argument("--wordlist", default=DEFAULT_WORDLIST)
    parser.add_argument("--history", default=DEFAULT_HISTORY)
    parser.add_argument("--solved-list", default=DEFAULT_SOLVED_LIST)
    parser.add_argument("--session-log", default=DEFAULT_SESSION_LOG)

    parser.add_argument("--global-strength", type=float, default=5.0)
    parser.add_argument("--slot-strength", type=float, default=25.0)
    parser.add_argument("--structure-strength", type=float, default=0.35)
    parser.add_argument("--repeat-penalty", type=float, default=0.35)

    parser.add_argument("--frequency-threshold", type=int, default=3500)
    parser.add_argument("--exact-threshold", type=int, default=14)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--send-delay", type=float, default=0.002)
    parser.add_argument("--reconnect-delay", type=float, default=1.0)

    parser.add_argument(
        "--once", action="store_true", help="Do not reconnect after disconnect"
    )
    parser.add_argument("--stats", action="store_true", help="Print learned stats and exit")
    parser.add_argument("--self-test", action="store_true", help="Run tests before playing")
    parser.add_argument("--test-only", action="store_true", help="Run tests and exit")
    parser.add_argument(
        "--reset-history", action="store_true", help="Delete persistent learning files"
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.reset_history:
        for path in (args.history, args.solved_list, args.session_log):
            try:
                Path(path).unlink()
                log(f"[RESET] Removed {path}")
            except FileNotFoundError:
                pass
            except OSError as error:
                log(f"[WARN] Cannot remove {path}: {error}")

    if args.self_test or args.test_only:
        self_test()
    if args.test_only:
        return 0

    server_id = f"{args.host}:{args.port}"
    learner = PersistentLearner(args.history, args.solved_list, server_id)

    if args.stats:
        print_stats(learner)
        return 0

    try:
        all_words = load_wordlist(args.wordlist)
    except OSError as error:
        log(f"[ERROR] Cannot read {args.wordlist}: {error}")
        return 1

    all_words = append_history_words(all_words, learner)
    if not all_words:
        log("[ERROR] Wordlist is empty")
        return 1

    log(f"[INIT] Loaded {len(all_words)} valid five-letter words")
    log(
        f"[MODEL] global={args.global_strength}, slot={args.slot_strength}, "
        f"structure={args.structure_strength}, repeat_penalty={args.repeat_penalty}"
    )

    session_log = SessionLogger(args.session_log)

    while True:
        try:
            play_connection(args, learner, session_log, all_words)
        except KeyboardInterrupt:
            log("\n[STOP] Interrupted by user")
            return 0
        except (ConnectionError, TimeoutError, socket.timeout, OSError) as error:
            log(f"[NET] Connection ended: {error}")
        except Exception as error:
            log(f"[ERROR] Unexpected failure: {type(error).__name__}: {error}")
            if args.once:
                raise

        if args.once:
            return 0
        log(f"[NET] Reconnecting in {args.reconnect_delay:.1f}s...")
        time.sleep(args.reconnect_delay)


if __name__ == "__main__":
    sys.exit(main())
