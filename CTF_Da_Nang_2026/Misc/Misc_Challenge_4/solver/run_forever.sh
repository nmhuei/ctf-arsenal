#!/usr/bin/env bash
# Supervisor: keeps the solver alive until the flag is captured.
# - Solver exits 0        -> flag/token found, stop everything.
# - Any other exit code   -> log it, cool down, relaunch.
# - Instance fully offline-> solver exits 3; supervisor keeps polling
#                            (cheap) so recovery is automatic after a
#                            platform-side container restart.

URL="https://9e1dd596-b52e-40eb-aacd-5adb3e3fd2db.222.255.138.122.nip.io"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$DIR/solver/solve_fast.log"
STATE="$DIR/solver/state.json"

cd "$DIR"
round=0
while true; do
    round=$((round + 1))
    echo "[supervisor $round $(date '+%F %T')] launching solver" >> "$LOG"
    python3 solver/solve.py "$URL" --state "$STATE" --watch \
        --delay 4.0 --min-delay 3.0 --max-delay 9.0 >> "$LOG" 2>&1
    code=$?
    echo "[supervisor $round $(date '+%F %T')] solver exited code=$code" >> "$LOG"
    if [ "$code" -eq 0 ]; then
        echo "[supervisor] FLAG CAPTURED - shutting down." >> "$LOG"
        break
    fi
    sleep 45
done
