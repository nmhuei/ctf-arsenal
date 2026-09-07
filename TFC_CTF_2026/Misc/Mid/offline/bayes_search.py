#!/usr/bin/env python3
"""Offline noisy threshold search; requires numpy. No network access."""

import argparse
import numpy as np


def simulate(secrets, flips, size, noise, confidence):
    """Maintain P(secret | answers), stopping at confidence or query budget.

    Each answer is the Boolean `secret <= threshold`, independently flipped
    with known probability noise. There is no separate equality response.
    """
    trials = len(secrets)
    posterior = np.full((trials, size), 1.0 / size)
    active = np.ones(trials, dtype=bool)
    counts = np.zeros(trials, dtype=int)
    for step in range(len(flips)):
        rows = np.flatnonzero(active)
        if not len(rows):
            break
        current = posterior[rows]
        cumulative = current.cumsum(axis=1)
        threshold = np.abs(cumulative[:, :-1] - 0.5).argmin(axis=1)
        answer = (secrets[rows] <= threshold) ^ flips[step, rows]
        matches = (np.arange(size)[None, :] <= threshold[:, None]) == answer[:, None]
        current *= np.where(matches, 1 - noise, noise)
        current /= current.sum(axis=1, keepdims=True)
        posterior[rows] = current
        counts[rows] += 1
        # None means a strict fixed-budget baseline.
        if confidence is not None:
            active[rows] = current.max(axis=1) < confidence
    estimates = posterior.argmax(axis=1)
    return estimates == secrets, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, default=128)
    parser.add_argument('--trials', type=int, default=10000)
    parser.add_argument('--budget', type=int, default=21)
    parser.add_argument('--noise', type=float, default=0.1)
    parser.add_argument('--confidence', type=float, default=0.99)
    parser.add_argument('--seed', type=int, default=20260908)
    args = parser.parse_args()
    if args.size < 2 or args.trials < 1 or args.budget < 1:
        parser.error('size >= 2, trials >= 1 and budget >= 1 are required')
    if not 0 <= args.noise < 0.5:
        parser.error('noise must be in [0, 0.5)')
    if not 0 < args.confidence <= 1:
        parser.error('confidence must be in (0, 1]')
    rng = np.random.default_rng(args.seed)
    secrets = rng.integers(args.size, size=args.trials)
    flips = rng.random((args.budget, args.trials)) < args.noise
    print(f'Offline: size={args.size}, trials={args.trials}, noise={args.noise}, seed={args.seed}')
    print('method,success_percent,mean_queries')
    for name, confidence in [('fixed_budget', None), ('early_stop', args.confidence)]:
        correct, counts = simulate(secrets, flips, args.size, args.noise, confidence)
        print(f'{name},{100 * correct.mean():.2f},{counts.mean():.2f}')


if __name__ == '__main__':
    main()
