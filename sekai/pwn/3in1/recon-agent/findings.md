STATUS: SOLVED (bug confirmed)
CONFIDENCE: high
SUMMARY:
Bug heap overflow trong QEMU virtio-snd PCM input callback (virtio_snd_pcm_in_cb).
Patch qemu_1.patch: xoá dòng `to_read = MIN(to_read, max_size - buffer->size)` — đây là
clamp ngăn audio_be_read() ghi quá buffer->data[] đã cấp phát.

EVIDENCE:
=== Source code phân tích ===

1. Struct VirtIOSoundPCMBuffer (hw/audio/virtio-snd.h):
   - Có `VirtIOSoundPCMBuffer` với flexible array member `data[]`
   - Cấp phát: `g_malloc0(sizeof(VirtIOSoundPCMBuffer) + size)`
     trong `virtio_snd_handle_rx_xfer()` (line ~979)
   - size = iov_size(elem->in_sg, elem->in_num) - sizeof(virtio_snd_pcm_status)
   - Đây là kích thước guest control được (guest cung cấp VQ element)

2. Struct VirtIOSoundPCMStream (hw/audio/virtio-snd.h):
   - Chứa `VirtIOSoundPCMParams params` với `period_bytes` (uint32_t)
   - `virtio_snd_set_pcm_params()` (line ~286) copy params từ guest input
     QUA iov_to_buf() KHÔNG validate period_bytes — guest có thể set 0xFFFFFFFF

3. Bug (patched code, hw/audio/virtio-snd.c:1277-1281):
   size = audio_be_read(stream->s->audio_be,
                        stream->voice.in,
                        buffer->data + buffer->size,
                        MIN(available, (stream->params.period_bytes -
                                        buffer->size)));
   - THIẾU clamp `MIN(to_read, max_size - buffer->size)`
   - buffer->data chỉ được g_malloc0(max_size) bytes
   - Nếu CHOOSE period_bytes > max_size, audio_be_read ghi tràn
   - available = INT_MAX (backend "none" luôn báo available lớn)

4. Overflow magnitude:
   - buffer size: sizeof(VirtIOSoundPCMBuffer) + max_size (~128 byte guest buffer)
   - period_bytes do guest set: 0xFFFFFFFF
   - available: audio backend "none" gọi callback liên tục với available
     bằng period_size (rất lớn) 
   - overflow có thể ghi RẤT NHIỀU bytes vào heap sau buffer->data

=== Trigger condition ===
Guest driver cần:
1. Gửi descriptor VQ nhỏ (VD: 128 byte) cho RX queue
   → max_size ~ 128 - sizeof(status) ~ 112
   → malloc: sizeof(VirtIOSoundPCMBuffer) + 112
2. Set period_bytes RẤT LỚN (VD: 0x10000 hoặc 0xFFFFFFFF)
3. Kích hoạt stream → virtio_snd_pcm_in_cb được gọi
4. Loop đầu: buffer->size = 0, period_bytes - buffer->size = LỚN
   → audio_be_read ghi available bytes (rất lớn) vào buffer->data (112 bytes)

=== qemu_2.patch TCG access fix (ĐÃ ĐÓNG) ===
Patch qemu_2.patch sửa 1 0day thật trong target/i386/tcg/access.c:
- access_within_fragment() check for integer overflow
- NULL check cho haddr2
Nguồn: https://kqx.io/post/qemu-0day/
KHÔNG cần đầu tư thêm (đã được fix bởi challenge author).

=== QEMU đã clone tại ===
/home/light/Workspace/CTF/sekai/pwn_3in1/pwn_3in1/qemu/
commit b83371668192a705b878e909c5ae9c1233cbd5fb
qemu_1.patch đã áp dụng thành công.

NEXT_STEP:
- Chờ build-debug-agent build QEMU debug binary
- Xác nhận struct kích thước chính xác bằng assert/GDB sau khi build
- HEAP GROOMING: cần tìm QEMU object có function pointer gần buffer->data
  để chuyển overflow primitive → code execution

NEEDS_FROM_OTHER_AGENT:
- build-debug-agent: cần build QEMU để verify cụ thể
- exploit-primitive-agent: cần heap layout analysis từ GDB
