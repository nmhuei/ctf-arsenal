#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest


SOLVER = pathlib.Path(__file__).parents[1] / "solver" / "solve.py"
spec = importlib.util.spec_from_file_location("self_service_solver", SOLVER)
solver = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(solver)


class SolverHelpersTest(unittest.TestCase):
    def test_extract_flag_ignores_terminal_noise(self):
        output = "ops@srv2:~$ cat /home/ops/flag.txt\r\nNNS{demo_flag}\r\nops@srv2:~$"
        self.assertEqual(solver.extract_flag(output), "NNS{demo_flag}")

    def test_moddn_ldif_preserves_old_attribute_when_requested(self):
        self.assertEqual(
            solver.moddn_ldif("uid=old,ou=staff,dc=corp,dc=nns", "uid=new", False),
            "dn: uid=old,ou=staff,dc=corp,dc=nns\n"
            "changetype: moddn\n"
            "newrdn: uid=new\n"
            "deleteoldrdn: 0\n",
        )

    def test_replace_ldif_builds_a_single_attribute_change(self):
        self.assertEqual(
            solver.replace_ldif("uid=ops,ou=staff,dc=corp,dc=nns", "userPassword", "pw"),
            "dn: uid=ops,ou=staff,dc=corp,dc=nns\n"
            "changetype: modify\n"
            "replace: userPassword\n"
            "userPassword: pw\n",
        )

    def test_final_actor_is_identified_by_the_taken_over_dn(self):
        self.assertTrue(solver.is_final_actor("agrant", solver.FINAL_DN))
        self.assertFalse(solver.is_final_actor("ereid", solver.FINAL_DN))

    def test_srv2_prompt_detection_uses_the_remote_host(self):
        self.assertTrue(solver.has_srv2_prompt("ops@srv2-abc:~$ "))
        self.assertFalse(solver.has_srv2_prompt("agrant@jump:~$ "))


if __name__ == "__main__":
    unittest.main()
