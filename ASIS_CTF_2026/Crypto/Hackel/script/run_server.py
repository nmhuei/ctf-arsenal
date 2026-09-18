#!/usr/bin/env python3
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHALL_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "challenge", "Hackel")

env = os.environ.copy()
env["PYTHONPATH"] = SCRIPT_DIR + (":" + env["PYTHONPATH"] if "PYTHONPATH" in env else "")

port = sys.argv[1] if len(sys.argv) > 1 else "13373"

cmd = [sys.executable, os.path.join(CHALL_DIR, "hackel.py"), "--host", "127.0.0.1", "--port", str(port)]
subprocess.run(cmd, env=env)
