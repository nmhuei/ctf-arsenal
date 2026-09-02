#!/bin/sh
set -e

if [ -z "$OAUTH_SECRET" ]; then
    echo "OAUTH_SECRET not set, using default test flag"
    OAUTH_SECRET='flag{fak3_fl4g_f0r_t3st1ng}'
fi

API_KEY=$(printf '%s' "api-auth" | openssl dgst -sha256 -hmac "$OAUTH_SECRET" -hex | sed 's/.*= //' | cut -c1-16)
ADMIN_TOKEN=$(openssl rand -hex 32)

cat > .env <<EOF
OAUTH_SECRET=$OAUTH_SECRET
API_KEY=$API_KEY
ADMIN_TOKEN=$ADMIN_TOKEN
PROXY_PORT=${PROXY_PORT:-3000}
BOT_PORT=${BOT_PORT:-8000}
SITE=${SITE:-http://proxy:3000}
EOF

exec docker compose up "$@"
