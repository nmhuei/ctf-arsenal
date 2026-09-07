#!/usr/bin/env python3
"""Pwntools solver for TFC CTF 2026 - Misc / Mid."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import string
import threading
import time
from pathlib import Path

from pwn import context, log, remote

from switch_bayes import SwitchBayes


PASSWORD_LENGTH = 30
MAX_QUERIES = 195
ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
TOTAL = 62**PASSWORD_LENGTH
FLAG_RE = re.compile(rb"(?:TFCCTF|FLAG)\{[^}\r\n]+\}")


def num_to_str(num: int) -> str:
    chars = []
    for _ in range(PASSWORD_LENGTH):
        chars.append(ALPHABET[num % 62])
        num //= 62
    return "".join(reversed(chars))


def recv_prompt(io, timeout: float) -> bytes:
    """Receive one response and the next ``> `` prompt."""
    data = io.recvuntil(b"> ", timeout=timeout)
    if not data:
        raise TimeoutError(f"no response after {timeout:g}s")
    return data


def solve_attempt(host: str, port: int, timeout: float, worker_id: int, debug: bool) -> str | None:
    io = remote(host, port, ssl=True, timeout=timeout)
    try:
        # The challenge prints the three banner lines and then waits at `> `.
        banner = recv_prompt(io, timeout)
        log.info(
            "[W%d] received banner: %s",
            worker_id,
            banner.decode(errors="replace").replace("\r", "").replace("\n", " | "),
        )

        tracker = SwitchBayes(size=TOTAL, max_queries=MAX_QUERIES)
        for query_id in range(MAX_QUERIES):
            state = tracker.choose_state(query_id)
            guess_number = tracker.choose_guess(query_id, state)
            guess = num_to_str(guess_number)
            if query_id % 10 == 0:
                log.info(
                    "[W%d] Bayesian query %d/%d: state=%d guess=%s",
                    worker_id,
                    query_id + 1,
                    MAX_QUERIES,
                    state,
                    guess,
                )
            io.sendline(f"{state} {guess}".encode())

            response = recv_prompt(io, timeout)
            flag_match = FLAG_RE.search(response)
            if flag_match:
                return flag_match.group().decode()

            if b"smaller" in response:
                tracker.observe(query_id, state, guess_number, "smaller")
            elif b"larger" in response:
                tracker.observe(query_id, state, guess_number, "larger")
            else:
                return None

        return None
    finally:
        io.close()


def worker(worker_id: int, host: str, port: int, timeout: float, debug: bool, stop: threading.Event):
    attempt = 0
    while not stop.is_set():
        attempt += 1
        log.info("[W%d] attempt %d: waiting for banner (timeout=%gs)", worker_id, attempt, timeout)
        try:
            flag = solve_attempt(host, port, timeout, worker_id, debug)
        except (EOFError, OSError, TimeoutError) as exc:
            log.warning("[W%d] attempt %d failed: %s", worker_id, attempt, exc)
            continue

        if flag:
            stop.set()
            return flag

        log.info("[W%d] attempt %d had random oracle; reconnecting", worker_id, attempt)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=5, help="parallel solver connections (default: 5)")
    parser.add_argument("--debug", action="store_true", help="show every pwntools send/receive")
    args = parser.parse_args()

    if args.workers < 1:
        parser.error("--workers must be at least 1")

    context.log_level = "debug" if args.debug else "info"
    started = time.time()
    stop = threading.Event()
    log.info("starting %d parallel workers", args.workers)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(worker, worker_id, args.host, args.port, args.timeout, args.debug, stop)
            for worker_id in range(1, args.workers + 1)
        ]
        flag = None
        for future in as_completed(futures):
            result = future.result()
            if result:
                flag = result
                break

    if flag:
        log.success("flag found after %.1fs: %s", time.time() - started, flag)
        Path(__file__).resolve().parents[1].joinpath("flag.txt").write_text(flag + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
