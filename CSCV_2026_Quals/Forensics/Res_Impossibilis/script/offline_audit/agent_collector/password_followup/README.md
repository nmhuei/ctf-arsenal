# Original password follow-up

## Exact collector imports

`collector_dynsym.json` parses the 32 ELF64 dynamic symbols, including null. `rand` is real symbol 31 (name offset 0x47); `srand` is symbol 16. `printf` is also a real symbol. The compiler/linker shares suffixes in `.dynstr`, so substring presence alone was insufficient. No dynamic cryptographic-library imports appear. This does not exclude statically compiled password derivation. Only the verified 4096-byte first ELF page is available; no password-generation code or format string was recovered.

## Audit log extent

The 60-byte `/tmp/.mega_transfer_audit.log` inode is `ffff979067d175a0`. Its XFS in-core extent pointer at inode minus 0xc0 is `ffff978f466c7ca0`. The 16 bytes decode as file offset block 0, one allocated block, written state, start block `0x1019484`. The captured mount geometry has 4096-byte blocks, 4,587,520 blocks per allocation group, and AG block log 23. Therefore this is allocation group 2, block `0x19484`, linear filesystem block `0x8d9484`, or logical device sector `0x46ca420`. Device-mapper/partition offsets are not established. See `auditlog_extent.json` and `log_block_refs.py`.

A full memory scan for the 64-bit little- and big-endian representations of these three block addresses returned five hits. Two are accidental byte sequences spanning unrelated userspace pointers. Three are copies of XFS extent-free intent/done metadata (types 0x1236 and 0x1237) containing the exact encoded block and count 1. No logical-sector reference or buffer with the log contents was found. The metadata establishes a lifecycle record for that block but does not establish deletion timing or identify its prior owner. It does not recover any password bytes.

The structure layout and record type interpretation were checked against official Linux v5.14 XFS sources: https://raw.githubusercontent.com/torvalds/linux/v5.14/fs/xfs/libxfs/xfs_iext_tree.c and https://raw.githubusercontent.com/torvalds/linux/v5.14/fs/xfs/libxfs/xfs_log_format.h .

## Result

Original ZIP password remains unverified. This bounded extent-reference experiment is complete; no broader password guesses were introduced.
