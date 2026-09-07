#!/bin/sh
set -eu

python -m uvicorn main:app --app-dir /brain --host 127.0.0.1 --port 8000 &
brain_pid=$!

until python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" >/dev/null 2>&1; do
  if ! kill -0 "$brain_pid" 2>/dev/null; then
    wait "$brain_pid"
    exit 1
  fi
  sleep 1
done

node /app/src/server.js &
app_pid=$!

trap 'kill "$brain_pid" "$app_pid" 2>/dev/null || true; wait "$brain_pid" "$app_pid" 2>/dev/null || true' EXIT INT TERM

while kill -0 "$brain_pid" 2>/dev/null && kill -0 "$app_pid" 2>/dev/null; do
  sleep 1
done

exit 1
