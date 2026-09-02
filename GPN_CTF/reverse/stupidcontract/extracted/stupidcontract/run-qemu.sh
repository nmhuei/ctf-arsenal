#!/bin/sh
exec qemu-system-x86_64 \
              -M pc \
              -kernel images/patched.bzImage \
              -drive "file=rootfs.ext2,format=raw,if=virtio" \
              -append "rootwait root=/dev/vda console=ttyS0" \
              -nographic \
              -m 512 \
              -smp 2 \
              -virtfs local,path=/flag-data,mount_tag=shared,security_model=mapped-xattr
