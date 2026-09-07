import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import solve  # noqa: E402


class _Target:
    def close(self):
        pass


class RetryAfterTimeoutTest(unittest.TestCase):
    def _solve_with_patches(self, target_factory, attempt_results):
        with mock.patch.object(solve, "RemoteTarget", side_effect=target_factory), \
             mock.patch.object(solve, "attempt_solve", side_effect=attempt_results), \
             mock.patch.object(Path, "write_text"), \
             mock.patch.object(solve.sys, "argv", ["solve.py", "--remote", "host", "1337"]):
            return solve.solve()

    def test_remote_read_timeout_is_retried(self):
        targets = [_Target(), _Target()]

        def new_target(*_args, **_kwargs):
            return targets.pop(0)

        self.assertEqual(
            self._solve_with_patches(
                new_target,
                [TimeoutError("startup timed out"), "TFCCTF{test}"],
            ),
            "TFCCTF{test}",
        )

    def test_remote_connection_timeout_is_retried(self):
        targets = iter([TimeoutError("connect timed out"), _Target()])

        def new_target(*_args, **_kwargs):
            target = next(targets)
            if isinstance(target, Exception):
                raise target
            return target

        self.assertEqual(
            self._solve_with_patches(new_target, ["TFCCTF{test}"]),
            "TFCCTF{test}",
        )


class TLSTransportTest(unittest.TestCase):
    def test_remote_mode_enables_tls_by_default(self):
        target = _Target()
        calls = []

        def new_target(*args, **kwargs):
            calls.append((args, kwargs))
            return target

        with mock.patch.object(solve, "RemoteTarget", side_effect=new_target), \
             mock.patch.object(solve, "attempt_solve", return_value="TFCCTF{test}"), \
             mock.patch.object(Path, "write_text"), \
             mock.patch.object(solve.sys, "argv", ["solve.py", "--remote", "host", "1337"]):
            solve.solve()

        self.assertEqual(
            calls,
            [(('host', 1337), {"use_ssl": True, "timeout": solve.DEFAULT_REMOTE_TIMEOUT})],
        )

    def test_remote_target_wraps_socket_with_unverified_tls(self):
        raw_socket = mock.Mock()
        tls_socket = mock.Mock()
        context = mock.Mock()
        context.wrap_socket.return_value = tls_socket

        with mock.patch("socket.create_connection", return_value=raw_socket), \
             mock.patch("ssl.create_default_context", return_value=context):
            target = solve.RemoteTarget("host", 1337, use_ssl=True)

        self.assertIs(target.sock, tls_socket)
        self.assertFalse(context.check_hostname)
        self.assertEqual(context.verify_mode, solve.ssl.CERT_NONE)
        context.wrap_socket.assert_called_once_with(raw_socket, server_hostname="host")


class TimeoutConfigurationTest(unittest.TestCase):
    def test_remote_cli_passes_custom_timeout_to_target(self):
        target = _Target()
        calls = []

        def new_target(*args, **kwargs):
            calls.append((args, kwargs))
            return target

        with mock.patch.object(solve, "RemoteTarget", side_effect=new_target), \
             mock.patch.object(solve, "attempt_solve", return_value="TFCCTF{test}"), \
             mock.patch.object(Path, "write_text"), \
             mock.patch.object(
                 solve.sys,
                 "argv",
                 ["solve.py", "--remote", "host", "1337", "--timeout", "120"],
             ):
            solve.solve()

        self.assertEqual(calls, [(('host', 1337), {"use_ssl": True, "timeout": 120.0})])

    def test_remote_target_uses_configured_socket_timeout(self):
        raw_socket = mock.Mock()

        with mock.patch("socket.create_connection", return_value=raw_socket) as create_connection:
            solve.RemoteTarget("host", 1337, use_ssl=False, timeout=120.0)

        create_connection.assert_called_once_with(("host", 1337), timeout=120.0)


if __name__ == "__main__":
    unittest.main()
