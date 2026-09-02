#!/bin/bash
# test_qemu_direct.sh — Test QEMU boot with empty payload
set -euo pipefail

PROJECT_ROOT="/home/light/Workspace/CTF/sekai/pwn_3in1/pwn_3in1"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"
PAYLOAD_FILE=$(mktemp)
WORKDIR="$PROJECT_ROOT/../work/shared"
POC_JS="$PROJECT_ROOT/../work/guest-runtime-agent/poc_min.js"

# Use PoC JS if exists, else create minimal payload
if [ -f "$POC_JS" ]; then
    cp "$POC_JS" "$PAYLOAD_FILE"
else
    echo "console.log('Hello from pwn_3in1 guest!');" > "$PAYLOAD_FILE"
fi

chmod 644 "$PAYLOAD_FILE"
echo "[*] Payload: $(wc -c < "$PAYLOAD_FILE") bytes"
echo "[*] QEMU: $ARTIFACTS_DIR/qemu-system-x86_64"
echo "[*] Starting QEMU (timeout: 30s)..."
echo "==============================================="

timeout 30 "$ARTIFACTS_DIR/qemu-system-x86_64" \
    -L "$ARTIFACTS_DIR/pc-bios" \
    -kernel "$ARTIFACTS_DIR/bzImage" \
    -cpu max,+smap,+smep,+fsgsbase \
    -smp 1 \
    -m 256M \
    -initrd "$ARTIFACTS_DIR/initramfs.cpio" \
    -append "console=ttyS0 quiet loglevel=3 oops=panic panic_on_warn=1 panic=-1 page_alloc.shuffle=1 rdinit=/init" \
    -no-reboot \
    -display none \
    -monitor none \
    -chardev stdio,id=serial0,signal=off,mux=off \
    -serial chardev:serial0 \
    -audiodev none,id=snd0,in.mixing-engine=off,out.mixing-engine=off,in.fixed-settings=off,out.fixed-settings=off,timer-period=10000 \
    -device virtio-sound-pci,audiodev=snd0,streams=4,ioeventfd=off \
    -drive format=raw,file="$PAYLOAD_FILE",if=virtio,readonly=on,cache=unsafe 2>&1 || true

echo "==============================================="
echo "[*] QEMU exit code: $?"
rm -f "$PAYLOAD_FILE"
