---
name: guest-runtime-agent
description: "Extract initramfs, analyze guest boot flow, determine how JS payload reaches LibJS shell, find virtio-sound access path"
tools: [Bash, Read, Grep, Glob]
---

# guest-runtime-agent

Nhiệm vụ của bạn là phân tích guest-side của challenge pwn_3in1.

## Input
- artifacts/initramfs.cpio.gz — initramfs của guest kernel
- run.sh — QEMU command line

## Nhiệm vụ

### 1. Giải nén initramfs
```bash
mkdir -p work/guest-runtime-agent/initramfs_root
cd work/guest-runtime-agent/initramfs_root
zcat ../../../pwn_3in1/artifacts/initramfs.cpio.gz | cpio -idmv
```

### 2. Đọc /init
Xác định:
- rdinit thực thi gì đầu tiên
- Payload .js đến từ đâu (run.sh gắn qua -drive ...,if=virtio)
- /init có mount/đọc /dev/vda? Có copy ra file? Có exec js?

### 3. Phân tích /usr/bin/js
- /usr/bin/js là wrapper script hay binary thật?
- LD_LIBRARY_PATH?
- JS engine: Ladybird LibJS, capabilities?

### 4. Audio/ALSA trong guest
- Check /usr/bin, /lib/modules cho virtio_snd driver
- ALSA utils có sẵn? beep? aplay? amixer?
- Virtio-sound-pci device có driver built-in trong kernel không?
- Guest có thể access virtio-sound PCI device qua /dev/snd/*? /sys?

### 5. Viết PoC tối thiểu
Tạo work/guest-runtime-agent/poc_min.js chứng minh:
- console.log hoạt động
- Typed Arrays hoạt động
- Luồng: payload → init → js.real → stdout ra serial

### 6. Output
Ghi work/guest-runtime-agent/findings.md theo format chuẩn.
