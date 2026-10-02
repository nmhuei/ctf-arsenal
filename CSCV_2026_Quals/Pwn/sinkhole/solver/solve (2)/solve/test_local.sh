#!/bin/bash
cd "$(dirname "$0")"
CHROME=/mnt/c/Users/Damwan21/Desktop/cscv/candidate/candidate/chrome/chrome
PORT=8777
rm -f srv.log
python3 -m http.server $PORT --bind 127.0.0.1 >srv.log 2>&1 &
SRV=$!
sleep 1
PROF=$(mktemp -d /tmp/prof-XXXX)
echo "=== running bot-equivalent command ==="
timeout -s KILL 90 "$CHROME" --headless=new --no-sandbox --disable-gpu \
  --disable-dev-shm-usage --user-data-dir="$PROF" \
  --enable-logging=stderr --log-level=0 \
  --js-flags="--no-memory-protection-keys --expose-cage-base" \
  "http://127.0.0.1:$PORT/exploit.html" 2>&1 \
  | grep -aE 'CONSOLE|Received signal' | sed 's/, source: http.*//' | head -20
kill $SRV 2>/dev/null
echo "=== server log (exfil hits) ==="
grep -a 'flag_is' srv.log || echo "(no exfil request seen)"
rm -rf "$PROF"
