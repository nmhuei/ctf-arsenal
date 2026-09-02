---
name: build-debug-agent
description: "Build QEMU with debug symbols at the correct commit + patches, verify behaviour matches release binary"
tools: [Bash, Read]
---

# build-debug-agent

Nhiệm vụ: Build QEMU debug binary giống hệt bản release (patches + config) nhưng giữ symbol.

## Input
- work/recon-agent/findings.md — commit hash + patch status
- pwn_3in1/qemu/ — QEMU source tree (đã clone)
- patches/qemu_1.patch, qemu_2.patch
- artifacts/qemu-system-x86_64 — binary release để so sánh

## Nhiệm vụ

### 1. Chuẩn bị source
- Vào QEMU source (work/shared/qemu-source/ or pwn_3in1/qemu/)
- Reset về commit đúng (git checkout -f)
- Áp CẢ HAI patch qemu_1.patch + qemu_2.patch (vì binary release có cả 2)

### 2. Build với debug
- Configure flags tối thiểu:
  --target-list=x86_64-softmmu
  --enable-debug (hoặc --extra-cflags="-Og -g")
- Audio backend: --audio-drv-list= (để audiodev=none hoạt động)
- Build: make -j$(nproc)

### 3. Verify
- So --version với binary release
- So -device help | grep virtio-sound-pci
- Thử boot với payload rỗng, so log output

### 4. Output
- Binary debug vào work/shared/qemu-debug/qemu-system-x86_64
- Ghi build flags vào work/build-debug-agent/findings.md
- Nếu build thất bại, báo DEAD_END với lý do chi tiết
