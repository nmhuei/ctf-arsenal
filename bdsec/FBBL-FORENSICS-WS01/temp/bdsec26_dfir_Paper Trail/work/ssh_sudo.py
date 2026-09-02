#!/usr/bin/env python3
import base64, sys, paramiko

HOST, PORT, USER, PASS = "127.0.0.1", 2222, "investigator", "1234"
cmd = sys.argv[1] if len(sys.argv) > 1 else "id"
encoded = base64.b64encode(cmd.encode()).decode()
remote = f"sudo -S -p '' bash -c \"echo {encoded} | base64 -d | bash\""
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=20)
stdin, stdout, stderr = client.exec_command(remote, timeout=300)
stdin.write(PASS + "\n")
stdin.flush()
sys.stdout.write(stdout.read().decode(errors="replace"))
err = stderr.read().decode(errors="replace")
if err.strip():
    sys.stderr.write("\n[STDERR]\n" + err)
client.close()
