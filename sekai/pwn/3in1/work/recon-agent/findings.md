STATUS: SOLVED
CONFIDENCE: high

SUMMARY:
The patch in qemu_1.patch removes a bounds check in virtio_snd_pcm_in_cb that capped audio_be_read() at (max_size - buffer->size). Without this check, a guest can set an arbitrarily large period_bytes (no validation) and submit small RX virtqueue buffers, causing a heap buffer overflow when audio_be_read() writes past the end of buffer->data[].

EVIDENCE:

1. Struct Sizes & Allocation (virtio-snd.h:104-122, virtio-snd.c:976-984)

   VirtIOSoundPCMBuffer is allocated dynamically in virtio_snd_handle_rx_xfer():
       hw/audio/virtio-snd.c:976-984
       size = iov_size(elem->in_sg, elem->in_num) - sizeof(virtio_snd_pcm_status);
       buffer = g_malloc0(sizeof(VirtIOSoundPCMBuffer) + size);
       buffer->size = 0;  // tracks bytes written into data[]
   The flexible array member buffer->data[] has 'size' bytes of space.

   max_size is computed in virtio_snd_pcm_in_cb:
       hw/audio/virtio-snd.c:1265-1270
       max_size = iov_size(buffer->elem->in_sg, buffer->elem->in_num);
       max_size -= sizeof(virtio_snd_pcm_status);
   So max_size equals the 'size' used in the allocation above.

2. The Missing Bounds Check (Patch Context)

   Original code (pre-patch) at the same commit had three safety lines:
       to_read = stream->params.period_bytes - buffer->size;
       to_read = MIN(to_read, available);
       to_read = MIN(to_read, max_size - buffer->size);   // <-- THIS LINE REMOVED

   Patched code (qemu_1.patch, hw/audio/virtio-snd.c:1277-1281):
       size = audio_be_read(stream->s->audio_be,
                            stream->voice.in,
                            buffer->data + buffer->size,
                            MIN(available, (stream->params.period_bytes -
                                            buffer->size)));

   The third MIN() that capped to_read at (max_size - buffer->size) is gone.
   audio_be_read() can now write up to (period_bytes - buffer->size) bytes,
   regardless of how large period_bytes is relative to the buffer capacity.

3. No Validation of period_bytes (virtio-snd.c:256-294)

   hw/audio/virtio-snd.c:285-286
       st_params->period_bytes = le32_to_cpu(params->period_bytes);
       st_params->buffer_bytes = le32_to_cpu(params->buffer_bytes);

   Only channels, format, and rate are validated. period_bytes is stored
   directly without any upper bound check, so the guest can set it to any
   uint32_t value (up to UINT32_MAX = 0xFFFFFFFF).

4. Overflow Mechanism

   In the loop at virtio-snd.c:1272-1295:
   - First iteration: buffer->size = 0, so audio_be_read gets to read
     MIN(available, period_bytes - 0) bytes into buffer->data[].
   - If period_bytes > max_size and available >= period_bytes, the read
     overflows past the end of data[].
   - The check "if (buffer->size >= max_size)" at line 1273 only catches
     overfill AFTER the first read has already happened -- it cannot prevent
     the initial overflow.

5. Overflow Magnitude

   - Guest RX buffer can be as small as sizeof(virtio_snd_pcm_status) + 1 bytes
     (~21 bytes), giving max_size = 1 byte.
   - period_bytes can be set to 0xFFFFFFFF (UINT32_MAX).
   - audio_be_read() returns at most 'available' bytes (provided by the audio
     backend, e.g., PulseAudio, ALSA, or file backend).

   Worst-case overflow per callback invocation:
       MIN(available, period_bytes) - max_size
   which could be up to INT_MAX bytes in a single call.

6. Heap Memory Layout

   buffer = g_malloc0(sizeof(VirtIOSoundPCMBuffer) + size)
   Overflow from buffer->data[] writes into the adjacent heap chunk.

NEXT_STEP:
- Identify which audio backend the challenge environment uses to bound the
  realistic 'available' values.
- Design heap grooming to place useful objects (e.g., VirtQueueElement with
  function pointers, other VirtIOSoundPCMBuffer entries) adjacent to the
  overflowed buffer.

NEEDS_FROM_OTHER_AGENT:
- From build-debug-agent: QEMU binary info (compiler flags, heap allocator)
- From exploit-primitive-agent: Target heap layout analysis, useful adjacent
  objects for overwrite

================================================================================
GUEST KERNEL CONFIG (extracted from bzImage)
================================================================================

KERNEL: 6.1.176, gcc 15.2.0, BuildID f359e74ee130e74c7f92c0ee471d1de6df4acf3c
STATUS: .config NOT embedded (CONFIG_IKCONFIG=n), inferred from binary strings

CRITICAL KERNEL FEATURES:
  KASLR:               NOT ENABLED (fixed kernel base -- major advantage)
  SMAP:                ENABLED (-cpu max,+smap)
  SMEP:                ENABLED (-cpu max,+smep)
  FSGSBASE:            ENABLED (-cpu max,+fsgsbase)
  PTI (KPTI):          LIKELY ENABLED (default on x86_64)
  Retpolines:          ENABLED (Spectre v2)
  seccomp:             AVAILABLE
  User Namespaces:     ENABLED
  IMA:                 NOT ENABLED
  BPF/JIT:             NOT ENABLED
  /dev/mem,/dev/kmem:  NOT ENABLED
  SLAB:                SLUB allocator, slab merging default enabled
  page_alloc.shuffle=1: ENABLED (randomizes page freelist order)

KERNEL CRASH POLICY (from boot params):
  oops=panic panic_on_warn=1 panic=-1
  => Any kernel warning or oops => immediate panic => stuck forever

QEMU CONFIG:
  QEMU: 11.0.50 (v11.0.0-2279-gb833716681-dirty), DEBUG build, not stripped
  Audio backend: "none" (null backend, no ALSA/PulseAudio)
  audio_be_read() from null backend likely returns 0 or minimal bytes
  => Overflow magnitude in virtio_snd_pcm_in_cb is bounded by null backend

GUEST KERNEL VIRTIO DRIVERS:
  virtio-core:  ENABLED
  virtio-pci:   ENABLED (modern + legacy)
  virtio-blk:   ENABLED
  virtio-snd:   NOT FOUND (no driver in guest kernel at all)
  => Guest must interact with virtio-sound via raw PCI MMIO from userspace

Full config report: /tmp/kernel_config.txt
