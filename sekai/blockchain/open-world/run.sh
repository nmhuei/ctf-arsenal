#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Step 1: Get session (PoW) ==="
python3 get_session.py > session.json 2>pow.log
cat pow.log | grep -v "^\[PoW\] Tried"
echo "Session saved to session.json"

echo ""
echo "=== Step 2: Solve challenge (TON) ==="
npx ts-node solve_ton.ts 2>&1
