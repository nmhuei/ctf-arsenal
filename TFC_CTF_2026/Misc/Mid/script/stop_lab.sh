#!/usr/bin/env bash
set -euo pipefail
docker rm -f mid-lab 2>/dev/null && echo "[+] mid-lab stopped" || echo "[*] mid-lab not running"
