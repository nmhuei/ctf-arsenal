#!/usr/bin/env bash
set -euo pipefail

CHAL_DIR="${1:-scanwich-station}"
FLAG_VALUE="${FLAG_VALUE:-GPNCTF{local_test_flag}}"

cd "$CHAL_DIR"

if command -v docker >/dev/null 2>&1; then
  echo "[+] Docker found: building challenge image"
  docker build --load --target challenge --build-arg FLAG="$FLAG_VALUE" -t scanwich-station:local .
  echo "[+] Running local service on http://127.0.0.1:5002"
  docker rm -f scanwich-station-local >/dev/null 2>&1 || true
  docker run --rm --name scanwich-station-local -p 127.0.0.1:5002:5000 scanwich-station:local
else
  echo "[-] Docker not found. Compiling qrscan/read_flag only."
  mkdir -p /tmp/scanwich-station-local/dist
  clang -O2 -DNDEBUG -Ivendor/quirc/lib -D_FORTIFY_SOURCE=3 \
    -fPIE -fstack-protector-all -fstack-clash-protection -fcf-protection=full \
    -Wall -Wextra -Wpedantic \
    src/qrscan.c vendor/quirc/lib/quirc.c vendor/quirc/lib/decode.c \
    vendor/quirc/lib/identify.c vendor/quirc/lib/version_db.c \
    -pie -Wl,-z,relro -Wl,-z,noexecstack -Wl,-z,separate-code \
    -o /tmp/scanwich-station-local/dist/qrscan -lm
  clang -O2 -DNDEBUG -D_FORTIFY_SOURCE=3 \
    -fPIE -fstack-protector-all -fstack-clash-protection -fcf-protection=full \
    -Wall -Wextra -Wpedantic src/read_flag.c \
    -pie -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -Wl,-z,separate-code \
    -o /tmp/scanwich-station-local/read_flag
  echo "[+] Built: /tmp/scanwich-station-local/dist/qrscan"
  echo "[+] Built: /tmp/scanwich-station-local/read_flag"
  echo "[!] To run the real web service, use Docker or install: python3-flask python3-pil python3-png python3-pyzbar util-linux"
fi
