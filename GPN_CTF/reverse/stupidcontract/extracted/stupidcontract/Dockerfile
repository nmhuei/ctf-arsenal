FROM docker.io/library/ubuntu AS challenge

# Install apt dependencies if needed
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y socat bash ruby libguestfs-tools openssh-client qemu-system-aarch64 && apt-get clean

COPY images/patched.bzImage images/
COPY rootfs.ext2 .
COPY run-qemu.sh .

EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./run-qemu.sh,stderr"]
