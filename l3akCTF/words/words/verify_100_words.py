#!/usr/bin/env python3
"""Quick speed + accuracy benchmark on 100 words."""
from solve import load_wordlist, choose_guess, feedback_code, PersistentLearner, PromptState
import argparse, random, time, multiprocessing

words = load_wordlist('words.txt')
learner = PersistentLearner('wordguest_history.json', 'solved_words.txt', 'test_server')
parser = argparse.ArgumentParser()
parser.add_argument('--global-strength', type=float, default=1.25)
parser.add_argument('--slot-strength', type=float, default=3.0)
parser.add_argument('--structure-strength', type=float, default=0.35)
parser.add_argument('--repeat-penalty', type=float, default=0.35)
parser.add_argument('--frequency-threshold', type=int, default=3500)
parser.add_argument('--exact-threshold', type=int, default=20)
args = parser.parse_args([])

def solve_one(item):
    idx, target = item
    candidates = list(words)
    guessed, guess_seq, turns = set(), [], 0
    while True:
        turns += 1
        state = PromptState(round_id=999, word_id=idx, total_words=100, guess_no=turns)
        guess = choose_guess(candidates, words, state, learner, set(), guessed, args)
        guessed.add(guess); guess_seq.append(guess)
        if guess == target:
            return idx, target, turns, guess_seq
        code = feedback_code(guess, target)
        candidates = [w for w in candidates if feedback_code(guess, w) == code]

random.seed(2026)
learned = learner.known_words()
targets = random.sample(learned, 100) if len(learned) >= 100 else learned + random.sample(words, 100 - len(learned))

t0 = time.time()
with multiprocessing.Pool() as pool:
    results = pool.map(solve_one, list(enumerate(targets, 1)))
t1 = time.time()

results.sort(key=lambda x: x[0])
total = sum(r[2] for r in results)
dist = {}
for r in results:
    dist[r[2]] = dist.get(r[2], 0) + 1

print(f"Time: {t1-t0:.2f}s | Total guesses: {total} | Avg: {total/100:.2f}")
print(f"Distribution: {', '.join(f'{k}t:{dist[k]}' for k in sorted(dist))}")
print(f"Status: {'PASS' if total < 400 else 'FAIL'}")
