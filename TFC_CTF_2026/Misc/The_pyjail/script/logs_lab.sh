#!/usr/bin/env bash
CONTAINER_NAME="pyjail-lab"
echo "[*] Tailing logs for ${CONTAINER_NAME} (Ctrl+C to exit)..."
docker logs -f "${CONTAINER_NAME}"
