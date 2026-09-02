#!/usr/bin/env python3
import sys, paramiko

HOST, PORT, USER, PASS = "127.0.0.1", 2222, "investigator", "1234"

def run(cmd):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PASS, timeout=20)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=300)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    c.close()
    return out, err

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "id; hostname"
    out, err = run(cmd)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write("\n[STDERR]\n" + err)
