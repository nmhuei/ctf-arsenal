#!/usr/bin/env bash
set -e

PORT=${1:-1337}
CONTAINER_NAME="pyjail-lab"
FLAG=${2:-"TEST{local_pyjail_master_pwned_1337}"}

echo "[*] Setting up local PyJail Lab on port ${PORT}..."
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${PORT}:1234" \
  --restart unless-stopped \
  pyjail-lab:latest

# Update flag in container
docker exec "${CONTAINER_NAME}" bash -c "printf '%s\n' '${FLAG}' > /flag.txt && chmod 400 /flag.txt"

echo "[+] Lab is running!"
echo "    Container : ${CONTAINER_NAME}"
echo "    Port      : 127.0.0.1:${PORT}"
echo "    Flag      : ${FLAG}"
echo "    Logs      : ./script/logs_lab.sh"
echo "    Shell     : ./script/shell.py"
