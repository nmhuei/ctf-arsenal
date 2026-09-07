#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-1338}"
NAME="mid-lab"
DIR="$(cd "$(dirname "$0")/../challenge" && pwd)"

# Stop existing container if running
docker rm -f "$NAME" 2>/dev/null || true

echo "[*] Building $NAME image..."
docker build --load -t "$NAME:latest" "$DIR"

echo "[*] Starting $NAME on 127.0.0.1:$PORT -> 1338/tcp"
docker run -d \
  --name "$NAME" \
  -p "127.0.0.1:${PORT}:1338" \
  --restart unless-stopped \
  "$NAME:latest"

echo "[+] $NAME running. Connect: nc 127.0.0.1 $PORT"
echo "[+] Solve:  python3 solver/solve.py --remote 127.0.0.1 $PORT --plain"
