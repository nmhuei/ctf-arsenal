#!/usr/bin/env bash
set -u

cd "$(dirname "$0")"

HOST="${1:-challs.pyjail.club}"
PORT="${2:-20219}"
LOG="remote_server_$(date +%Y%m%d_%H%M%S).log"

cat <<MSG
[+] Working dir: $(pwd)
[+] Target: $HOST:$PORT
[+] Log file: $LOG
[+] Expected runtime: about 3-5 minutes if the remote socket stays alive
[+] If the server says 'remote closed before the first prompt', wait 30-60s and rerun this script.
MSG

if ! command -v jq >/dev/null 2>&1; then
  echo "[-] jq not found in PATH. Install jq-1.8.2 or run inside the prepared environment." | tee "$LOG"
  exit 1
fi

echo "[+] jq version: $(jq --version)" | tee -a "$LOG"

if [ ! -f solve_remote_live.py ] || [ ! -f chains_225.json ]; then
  echo "[-] Missing solve_remote_live.py or chains_225.json in $(pwd)" | tee -a "$LOG"
  exit 1
fi

# Do not use exact-index local helpers on remote; they contain .[pos]/numbers and are blocked.
# This uses the whitelist-safe global set-oracle/CSP solver.
python3 -u solve_remote_live.py \
  --chains chains_225.json \
  --min-length 100 \
  --max-length 128 \
  remote "$HOST" "$PORT" 2>&1 | tee -a "$LOG"

status=${PIPESTATUS[0]}
echo "[+] solver exit code: $status" | tee -a "$LOG"

echo "[+] Last 80 log lines:" | tee -a "$LOG"
tail -n 80 "$LOG"

exit "$status"
