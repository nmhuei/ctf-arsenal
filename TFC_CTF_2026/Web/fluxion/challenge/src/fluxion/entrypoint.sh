#!/bin/bash
set -e

# Ensure nginx temp/run dirs exist and are writable by the unprivileged user.
mkdir -p /tmp/nginx-client-body /tmp/nginx-proxy /tmp/nginx-fastcgi /tmp/nginx-uwsgi /tmp/nginx-scgi

# Start the Node app (loopback:8001) in the background.
node src/server.js &
APP_PID=$!

# Give the app a moment to bind before nginx starts proxying.
sleep 1

# Start nginx in the foreground as PID 1's child; if either dies, take the container down.
nginx -c /app/nginx.conf -g 'daemon off;' &
NGINX_PID=$!

# If either process exits, stop the other and exit.
wait -n "$APP_PID" "$NGINX_PID" 2>/dev/null || wait "$APP_PID" "$NGINX_PID"
kill "$APP_PID" "$NGINX_PID" 2>/dev/null || true
exit 1
