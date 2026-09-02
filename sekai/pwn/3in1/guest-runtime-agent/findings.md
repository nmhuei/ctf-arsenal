STATUS: IN_PROGRESS
CONFIDENCE: medium
SUMMARY:

### Boot Flow

1. Kernel boots with `rdinit=/init` (set in QEMU -append line).
2. `/init` (shell script, 518 bytes) is executed by the kernel as PID 1.
3. `/init` mounts proc, sysfs, devtmpfs, tmpfs.
4. Copies payload from `/dev/vda` (the virtio-blk drive) to `/home/user/challenge.js`.
5. Drops privileges via `exec su user -c '/usr/bin/js --disable-ansi-colors /home/user/challenge.js'`.
6. `/usr/bin/js` is a shell script wrapper that sets `LD_LIBRARY_PATH=/usr/lib/ladybird` and execs `/usr/bin/js.real`.
7. `/usr/bin/js.real` is the Ladybird LibJS standalone JS shell (ELF 64-bit LSB PIE x86-64, stripped, dynamically linked).

### rdinit executes first

```
/bin/sh /init
```

The kernel's `rdinit=/init` parameter causes it to execute `/init` as the first userspace process.

### Payload source

The payload arrives as a raw disk image attached via QEMU -drive:

```
-drive format=raw,file="$payload",if=virtio,readonly=on,cache=unsafe
```

This exposes the file as `/dev/vda` (virtio block device) inside the guest. `/init` copies it:

```sh
cat /dev/vda > /home/user/challenge.js
```

### /usr/bin/js architecture

- `/usr/bin/js` (124 bytes): shell script wrapper that sets `LD_LIBRARY_PATH` and exec's `js.real`.
- `/usr/bin/js.real` (114696 bytes): The actual Ladybird LibJS binary. Stripped.

### Patches applied (3 patches = "3in1" challenge name)

1. **qemu_1.patch** (virtio-snd): Removes `max_size` bounds check in `virtio_snd_pcm_in_cb`. Before: `to_read = MIN(to_read, max_size - buffer->size)`. After: removed. Could allow writing beyond buffer boundary in audio PCM input callback.

2. **qemu_2.patch** (TCG access fix): Fixes a QEMU 0-day in `target/i386/tcg/access.c`. Adds `access_within_fragment()` helper and NULL-check for `haddr2`. Reference: https://kqx.io/post/qemu-0day/

3. **ladybird_1.patch**: Removes `exit`, `help`, `save`, `loadINI`, `loadJSON`, `print` native functions from both `ReplObject` and `ScriptObject`. Only `gc` and console API remain.

### JS Engine Capabilities (available to exploit)

- Standard ECMA-262 JavaScript (full language semantics)
- `gc()` function (garbage collection trigger)
- `console.log()`, `console.error()`, etc. (ReplConsoleClient exists)
- `JSON.parse()` / `JSON.stringify()`
- Typed Arrays (Uint8Array, etc.)
- No `require()`, no `import`, no `fetch`, no `XMLHttpRequest`
- No `process`, no `Buffer`
- No filesystem or networking builtins exposed to JS

EVIDENCE:

### /init
```sh
#!/bin/sh
export PATH=/sbin:/bin:/usr/sbin:/usr/bin

mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mount -t tmpfs tmpfs /tmp 2>/dev/null || true
chmod 1777 /tmp 2>/dev/null || true

mkdir -p /home/user
chown user:user /home/user 2>/dev/null || true

cat /dev/vda > /home/user/challenge.js
chmod 0644 /home/user/challenge.js
chown user:user /home/user/challenge.js 2>/dev/null || true

exec su user -c '/usr/bin/js --disable-ansi-colors /home/user/challenge.js'
```

### /usr/bin/js (wrapper)
```sh
#!/bin/sh
export LD_LIBRARY_PATH=/usr/lib/ladybird:/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
exec /usr/bin/js.real "$@"
```

### Console output path
- `console.log(...)` -> stdout -> QEMU serial -> host's stdout (via `-chardev stdio,id=serial0`)

### readflag
- `/readflag` setuid binary (4511, root-owned) on the host, not inside initramfs.
- Takes two args: `/readflag sekai 3in1` and prints the flag.
- Compiled from `readflag.c`.

### Binaries/ALSA/audio tools available inside initramfs

- **Only busybox applets** (statically linked, ~2.5MB).
- **`beep`** - busybox applet for PC speaker beep.
- **No ALSA tools** (no aplay, arecord, alsamixer, amixer, speaker-test, etc.)
- **No ALSA libraries** in `/usr/lib/` or `/lib/`.
- Audio device: QEMU `virtio-sound-pci` (with `-audiodev none` - no host audio backend)

### Kernel boot parameters
```
console=ttyS0 quiet loglevel=3 oops=panic panic_on_warn=1 panic=-1 page_alloc.shuffle=1 rdinit=/init
```
- SMAP + SMEP enabled
- KASLR active (page_alloc.shuffle=1, no nokaslr)

### Host environment
- Runs in `ghcr.io/es3n1n/jail` container
- Process runs as user 1000
- Timeout: 180s (300s via docker-compose)
- Max payload: 2MB base64-encoded -> ~1.5MB raw JS
- `/readflag` setuid binary available on host

NEXT_STEP:
- Phan tich `js.real` binary de tim vulnerability (heap overflow, OOB, type confusion, UAF) trong LibJS engine
- Tao JS exploit gianh code execution ben trong VM
- Escape tu VM len host qua QEMU (virtio-snd hoac TCG access)
- Tren host chay `/readflag sekai 3in1`

NEEDS_FROM_OTHER_AGENT:
- Chua co
