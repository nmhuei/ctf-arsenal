#!/usr/bin/env bash
# Watchdog: runs from cron every 15 min. Ensures supervisor + solver alive,
# logs progress. Safe to run concurrently with everything (bracketed pgrep).

DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$DIR/solver/watchdog.log"
ts() { date '+%F %T'; }

if ! pgrep -f "[r]un_forever" >/dev/null 2>&1; then
    echo "[$(ts)] supervisor DEAD -> relaunching" >> "$LOG"
    cd "$DIR" || exit 1
    nohup bash solver/run_forever.sh > /dev/null 2>&1 &
    sleep 3
fi

if ! pgrep -f "[s]olve.py" >/dev/null 2>&1; then
    echo "[$(ts)] solver MISSING -> cycling supervisor" >> "$LOG"
    pkill -f "[r]un_forever" 2>/dev/null
    sleep 2
    cd "$DIR" || exit 1
    nohup bash solver/run_forever.sh > /dev/null 2>&1 &
fi

python3 - "$DIR/solver/state.json" >> "$LOG" <<'EOF'
import json, sys, datetime
try:
    s = json.load(open(sys.argv[1]))
    r = s.get("recovered", "")
    print(f"[{datetime.datetime.now():%F %T}] progress={len(r)}/48 recovered={r!r}")
except Exception as exc:
    print(f"[{datetime.datetime.now():%F %T}] state error: {exc}")
EOF
