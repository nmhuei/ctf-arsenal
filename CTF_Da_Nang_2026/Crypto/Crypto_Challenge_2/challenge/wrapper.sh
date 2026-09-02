#!/bin/sh
exec su -s /bin/sh app -c 'timeout --signal=KILL 120 prlimit --as=536870912 --fsize=1048576 python3 /opt/chall/server.py'
