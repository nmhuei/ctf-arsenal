import sys
import signal
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from switch_bayes import SwitchBayes  # noqa: E402


class SwitchBayesTest(unittest.TestCase):
    def test_guess_selection_scales_to_real_password_space(self):
        tracker = SwitchBayes(size=62**30, max_queries=195)

        def timeout(_signum, _frame):
            raise TimeoutError("guess selection enumerated the password space")

        previous = signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, 0.2)
        try:
            guess = tracker.choose_guess(0, 0)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)

        self.assertGreaterEqual(guess, 0)
        self.assertLess(guess, 62**30)

    def test_prefers_state_that_is_most_likely_truthful(self):
        tracker = SwitchBayes(size=8, max_queries=4)

        self.assertEqual(tracker.choose_state(0), 0)

        # At t=0, state 0 is truthful for switch_at >= 1.  This response
        # narrows all those branches to secrets below 3.
        tracker.observe(query_id=0, state=0, guess=3, response="larger")

        self.assertEqual(tracker.choose_state(1), 0)

    def test_switch_to_state_one_when_switch_branch_dominates(self):
        tracker = SwitchBayes(size=8, max_queries=4)

        # Repeated observations compatible with state 1 make the switch_at=0
        # branch the most likely one.
        for query_id in range(3):
            state, guess = 1, 3
            tracker.observe(query_id, state, guess, "smaller")

        self.assertEqual(tracker.choose_state(3), 1)

    def test_updates_secret_interval_for_truthful_branch(self):
        tracker = SwitchBayes(size=8, max_queries=4)
        tracker.observe(query_id=0, state=0, guess=3, response="larger")

        # All branches where state 0 was truthful must now contain only 0..2.
        for switch_at, interval in tracker.intervals().items():
            if switch_at >= 1:
                self.assertEqual(interval, (0, 2))


if __name__ == "__main__":
    unittest.main()
