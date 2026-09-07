#!/usr/bin/env bash
CONTAINER_NAME="pyjail-lab"
echo "[*] Stopping ${CONTAINER_NAME}..."
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
echo "[+] Lab stopped."
