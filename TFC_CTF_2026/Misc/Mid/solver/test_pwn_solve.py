import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import pwn_solve  # noqa: E402


class _FakeTube:
    def __init__(self):
        self.sent = []
        self.banner = True

    def recvuntil(self, marker, timeout=None):
        if self.banner:
            self.banner = False
            return b"Find the secret.\nlength = 30\nqueries = 195\n> "
        return b"TFCCTF{test}\n> "

    def sendline(self, data):
        self.sent.append(data)

    def send(self, data):
        self.sent.extend(data.splitlines())

    def close(self):
        pass


class PwnSolverIntegrationTest(unittest.TestCase):
    def test_attempt_starts_with_bayesian_state_choice(self):
        tube = _FakeTube()
        with mock.patch.object(pwn_solve, "remote", return_value=tube):
            flag = pwn_solve.solve_attempt("host", 1337, 1.0, 1, False)

        self.assertEqual(flag, "TFCCTF{test}")
        self.assertTrue(tube.sent)
        self.assertTrue(tube.sent[0].startswith(b"0 "))


if __name__ == "__main__":
    unittest.main()
