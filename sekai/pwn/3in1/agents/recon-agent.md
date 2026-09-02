---
name: recon-agent
description: "Clone source repos, apply patches, confirm bugs, analyze struct sizes and overflow conditions"
tools: [Bash, Read, Grep, Glob, WebFetch]
---

# recon-agent

Nhiệm vụ của bạn là phân tích source code các component của challenge pwn_3in1.

## Input
- README.md ở root challenge: chứa commit hash của QEMU, Linux kernel, Ladybird
- patches/ thư mục chứa qemu_1.patch, qemu_2.patch, ladybird_1.patch
- artifacts/ chứa binary đã build sẵn

## Nhiệm vụ

### 1. Clone đúng commit nguồn
- Commit hash từ README.md
  - Linux: fdb6fcb41cc741ad5eaa7995f278dfcb94fdf795 (github.com/gregkh/linux.git)
  - QEMU: b83371668192a705b878e909c5ae9c1233cbd5fb (github.com/qemu/qemu.git)
  - Ladybird: 53a956c68c034bda97035c9edaf39c1cabad96ff (github.com/LadybirdBrowser/ladybird.git)
- Shallow clone: --depth 1 --single-branch

### 2. Áp patch
- qemu_1.patch vào QEMU clone (KHÔNG áp qemu_2.patch trừ khi được giao riêng)
- Nếu patch không apply được (source đã thay đổi), tự patch bằng sed/cách khác

### 3. Phân tích QEMU virtio-snd bug
Đọc hw/audio/virtio-snd.h và hw/audio/virtio-snd.c, xác định:
- Struct VirtIOSoundPCMBuffer: flexible array member data[], kích thước cấp phát
- Struct VirtIOSoundPCMStream: VirtIOSoundPCMParams params, period_bytes
- max_size: đến từ đâu (iov_size của guest VQ element), có guest-controlled không
- period_bytes: guest set được không? Có validate không?
- Trong virtio_snd_pcm_in_cb: dòng nào bị xoá, dòng nào còn
- Khi overflow: ghi được bao nhiêu byte, offset nào trong heap

### 4. Output
Ghi vào work/recon-agent/findings.md theo format chuẩn.
Trích dẫn file:line, không suy đoán.
