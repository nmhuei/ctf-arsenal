STATUS: IN_PROGRESS
CONFIDENCE: medium
SUMMARY:
Scripts orchestration pipeline đã viết xong.
Chưa thể test vì Docker container (docker compose up) chưa chạy.

EVIDENCE:
=== Scripts ===
1. work/orchestration-infra-agent/send_payload.py
   - Protocol: TCP connect, read prompt, send base64, read stdout
   - Classification: flag/kernel_panic/qemu_crash/clean_exit/timeout/error
   - N iterations support (--n N)
   - Logging to work/shared/run_log.jsonl
   - Color output, summary table

2. work/orchestration-infra-agent/test_pipeline.sh
   - Quick test với payload rỗng ("//")
   - Kiểm tra kết nối qua nc hoặc /dev/tcp

=== Infrastructure notes ===
- Docker compose: docker-compose.yml listens port 5000
- Service chạy trong nsjail (JAIL_* envs)
- TIMEOUT=180s (300s qua docker compose)
- Cần privileged mode (docker --privileged)

=== Bypass các options ===
1. Dùng docker compose up -d
2. Hoặc chạy QEMU trực tiếp (skip Docker):
   cd pwn_3in1/artifacts
   echo "console.log('test')" > /tmp/payload.js  
   ./qemu-system-x86_64 -L ./pc-bios -kernel ./bzImage -cpu max,+smap,+smep,+fsgsbase \
     -smp 1 -m 256M -initrd ./initramfs.cpio \
     -append "console=ttyS0 quiet loglevel=3 oops=panic panic_on_warn=1 panic=-1 page_alloc.shuffle=1 rdinit=/init" \
     -no-reboot -display none -monitor none \
     -chardev stdio,id=serial0,signal=off,mux=off -serial chardev:serial0 \
     -audiodev none,id=snd0,in.mixing-engine=off,out.mixing-engine=off \
     -device virtio-sound-pci,audiodev=snd0,streams=4,ioeventfd=off \
     -drive format=raw,file=/tmp/payload.js,if=virtio,readonly=on,cache=unsafe

NEXT_STEP:
- Start Docker: docker compose -f pwn_3in1/docker-compose.yml up -d
- Chạy test script với payload rỗng

NEEDS_FROM_OTHER_AGENT:
- guest-runtime-agent: PoC JS payload
- recon-agent: confirm bug trigger path để thiết kế payload thật
