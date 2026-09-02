#!/usr/bin/env bash
# test_pipeline.sh — Verify the pwn_3in1 pipeline with an empty payload.
#
# Sends a minimal JS payload ("//" — just a comment, no-op) to verify:
#   - TCP connectivity to the runner container
#   - base64 decode → tempfile → run.sh → QEMU boot chain
#   - QEMU exits cleanly (or at least doesn't hang forever)
#
# Usage:
#   ./test_pipeline.sh [host] [port]
#
# Defaults: host=127.0.0.1 port=5000

set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-5000}"
TIMEOUT="${3:-60}"
PAYLOAD_B64="Ly8K"  # "//\n" in base64 — JS comment, no-op
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$(cd "$SCRIPT_DIR/../shared" && pwd)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="${LOG_DIR}/test_pipeline_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

echo "==============================================" | tee "$LOG_FILE"
echo " pwn_3in1 Pipeline Test — ${TIMESTAMP}"        | tee -a "$LOG_FILE"
echo " Target: ${HOST}:${PORT}"                       | tee -a "$LOG_FILE"
echo " Payload: ${PAYLOAD_B64} (empty JS comment)"    | tee -a "$LOG_FILE"
echo " Timeout: ${TIMEOUT}s"                           | tee -a "$LOG_FILE"
echo "==============================================" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# Step 1: Check if target is reachable
echo "[1/3] Checking TCP connectivity to ${HOST}:${PORT} ..." | tee -a "$LOG_FILE"
if timeout 5 bash -c "echo '' | nc -w 3 ${HOST} ${PORT} 2>/dev/null"; then
    echo "  -> Port is open!" | tee -a "$LOG_FILE"
else
    # nc might return non-zero if connection is reset after close; try a raw connect
    if timeout 5 bash -c "exec 3<>/dev/tcp/${HOST}/${PORT} 2>/dev/null"; then
        echo "  -> Port is open (bash /dev/tcp)!" | tee -a "$LOG_FILE"
        exec 3>&-
    else
        echo "  -> FAILED: Cannot connect to ${HOST}:${PORT}" | tee -a "$LOG_FILE"
        echo "     Is the Docker container running?" | tee -a "$LOG_FILE"
        echo "  -> docker ps | grep pwn_3in1"       | tee -a "$LOG_FILE"
        exit 1
    fi
fi
echo "" | tee -a "$LOG_FILE"

# Step 2: Send payload via send_payload.py
echo "[2/3] Sending empty payload via send_payload.py ..." | tee -a "$LOG_FILE"
PYTHON_CMD="python3"
if ! command -v python3 &>/dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &>/dev/null; then
    echo "  -> FAILED: python3 not found" | tee -a "$LOG_FILE"
    exit 1
fi

export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

"${PYTHON_CMD}" "${SCRIPT_DIR}/send_payload.py" \
    --base64 "${PAYLOAD_B64}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --timeout "${TIMEOUT}" \
    --log "${LOG_DIR}/run_log.jsonl" \
    -v 2>&1 | tee -a "$LOG_FILE"

RESULT="${PIPESTATUS[0]}"

echo "" | tee -a "$LOG_FILE"

# Step 3: Evaluate result
echo "[3/3] Evaluating result ..." | tee -a "$LOG_FILE"

if [ "$RESULT" -eq 0 ]; then
    echo "  -> Pipeline test completed (exit code 0)" | tee -a "$LOG_FILE"
else
    echo "  -> Pipeline test completed (exit code ${RESULT})" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Check log file for most recent entry
LAST_ENTRY=$(tail -1 "${LOG_DIR}/run_log.jsonl" 2>/dev/null | python3 -c "
import json, sys
try:
    r = json.loads(sys.stdin.read())
    print(f\"  result_class: {r.get('result_class', '?')}\")
    print(f\"  returncode:   {r.get('returncode', '?')}\")
    print(f\"  elapsed:      {r.get('elapsed', '?'):.1f}s\")
except Exception:
    print('  (no log entry)')
" 2>/dev/null || echo "  (no log entry)")

if [ -n "$LAST_ENTRY" ]; then
    echo "Last log entry:" | tee -a "$LOG_FILE"
    echo "$LAST_ENTRY" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "Test log saved to: ${LOG_FILE}" | tee -a "$LOG_FILE"
echo "Pipeline test complete." | tee -a "$LOG_FILE"
