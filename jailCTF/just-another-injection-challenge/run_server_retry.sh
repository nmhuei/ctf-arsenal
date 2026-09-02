#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"

HOST="${1:-challs.pyjail.club}"
PORT="${2:-20219}"
MAX_TRIES="${MAX_TRIES:-5}"
LOG="remote_server_retry_$(date +%Y%m%d_%H%M%S).log"

cat <<MSG | tee -a "$LOG"
[+] Working dir: $(pwd)
[+] Target: $HOST:$PORT
[+] Log file: $LOG
[+] Max tries: $MAX_TRIES
[+] Note: exit 143 means the local python solver received SIGTERM. If that happens, this wrapper retries after a short cooldown.
MSG

if ! command -v jq >/dev/null 2>&1; then
  echo "[-] jq not found in PATH" | tee -a "$LOG"
  exit 1
fi

echo "[+] jq version: $(jq --version)" | tee -a "$LOG"

for try in $(seq 1 "$MAX_TRIES"); do
  echo "" | tee -a "$LOG"
  echo "========== TRY $try / $MAX_TRIES ==========" | tee -a "$LOG"
  python3 -u solve_remote_live.py \
    --chains chains_225.json \
    --min-length 100 \
    --max-length 128 \
    remote "$HOST" "$PORT" 2>&1 | tee -a "$LOG"
  status=${PIPESTATUS[0]}
  echo "[+] solver exit code: $status" | tee -a "$LOG"

  if grep -E "\[\+\] (unique flag|recovered flag):|jail\{" "$LOG" | tail -n 20; then
    if grep -E "\[\+\] (unique flag|recovered flag):" "$LOG" >/dev/null; then
      echo "[+] flag-looking success line found, stopping retries." | tee -a "$LOG"
      exit 0
    fi
  fi

  if [ "$status" -eq 0 ]; then
    exit 0
  fi

  echo "[!] failed/terminated; cooldown before retry..." | tee -a "$LOG"
  sleep 45
done

echo "[-] all tries finished without clean success" | tee -a "$LOG"
echo "[+] Send this output back:" | tee -a "$LOG"
echo "tail -n 160 $LOG" | tee -a "$LOG"
exit 1
