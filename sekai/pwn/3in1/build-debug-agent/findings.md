## Agent: build-debug-agent

**STATUS**: COMPLETE

**CONFIDENCE**: HIGH

---

### SUMMARY

Built QEMU 11.0.50 from source (commit b83371668192a705b878e909c5ae9c1233cbd5fb) with both patches applied and debug symbols enabled.

**Patches applied:**
- `qemu_1.patch` (already applied before this agent ran) -- modifies `hw/audio/virtio-snd.c` (pcm_in_cb buffer read fix)
- `qemu_2.patch` (applied by this agent) -- modifies `target/i386/tcg/access.c` (adds `access_within_fragment` helper and fixes access_ptr bounds checks for QEMU 0day CVEs)

**Build details:**
- Configure: `./configure --target-list=x86_64-softmmu --enable-debug --extra-cflags="-Og -g" --audio-drv-list= --disable-werror` (with `--enable-fdt=disabled --ninja=/path/to/conda/ninja`)
- Build: ninja 3091/3091 targets
- Binary path (source): `/home/light/Workspace/CTF/sekai/pwn_3in1/pwn_3in1/qemu/build/qemu-system-x86_64`
- Binary size: 76,070,112 bytes
- File type: ELF 64-bit LSB pie executable, x86-64, dynamically linked, with debug_info, not stripped
- BuildID: 7205eb8a0fb0c5c41853604d60cff6130e973a23
- QEMU version: 11.0.50
- Device `virtio-sound-pci`: present

**Output copied to:** `/home/light/Workspace/CTF/sekai/pwn_3in1/work/shared/qemu-debug/qemu-system-x86_64`

**Dependencies notes:**
- `ninja-build` and `libfdt-dev` were not available from apt (no sudo). Installed via conda:
  - `ninja` from conda-forge
  - `libfdt` from conda-forge
- fdt was disabled at configure time (`--enable-fdt=disabled`) since x86_64-softmmu doesn't need it

### EVIDENCE

```
$ file qemu-system-x86_64
qemu-system-x86_64: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=7205eb8a0fb0c5c41853604d60cff6130e973a23, for GNU/Linux 3.2.0, with debug_info, not stripped

$ ./qemu-system-x86_64 --version
QEMU emulator version 11.0.50
Copyright (c) 2003-2026 Fabrice Bellard and the QEMU Project developers

$ ./qemu-system-x86_64 -device help 2>&1 | grep virtio-sound-pci
name "virtio-sound-pci", bus PCI, alias "virtio-sound", desc "Virtio Sound"
```

### NEXT_STEP

Ready for analysis/debugging. The debug binary is at:
`/home/light/Workspace/CTF/sekai/pwn_3in1/work/shared/qemu-debug/qemu-system-x86_64`

### NEEDS_FROM_OTHER_AGENT

None.
