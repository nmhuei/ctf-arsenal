#!/usr/bin/env python3
import sys, paramiko
HOST, PORT, USER, PASSWORD = "127.0.0.1", 2222, "investigator", "1234"
remote, local = sys.argv[1:3]
transport = paramiko.Transport((HOST, PORT))
transport.connect(username=USER, password=PASSWORD)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.get(remote, local)
sftp.close(); transport.close()
print(local)
