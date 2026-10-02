# Collector code recovery route audit

## Previously checked; not repeated

- Verified original first ELF page, damaged duplicate, exact build-ID copies, expected PLT patterns, and headers in all physical memory. No attributable text or rodata was recovered.
- Collector inode page-cache pointers and earlier mem.dmp cache copies were translated and verified. Text/rodata targets remained zero or nearly zero; current page metadata often reflects capture-time reuse by mem.dmp. This is not proof of deliberate wiping.
- 195 kernel page-table root candidates were checked at 0x400000 through 0x405000. Two map an unrelated executable. These candidates are not an enumeration of all historical processes.
- Exact imports are in collector_dynsym.json. gethostname, fgets, snprintf, srand and rand are genuine imports; there is no recovered call site proving their relation to password generation.

## New bounded checks

1. **Nonpresent PTE audit:** 1,170 walks (195 roots × six virtual pages) now record every terminating entry, including nonpresent entries. No walk ends at a nonpresent leaf PTE. Most terminate in absent upper levels; seven candidate roots contain nonzero, nonpresent top-level data, not interpretable swap entries. Thus no collector swap slot is identified by these roots. Evidence: collector_nonpresent_pte_audit.json.
2. **Stale VMA scan:** searched exact start/end pairs expected from the ELF LOAD segments: 400000–401000, 401000–403000, 403000–404000, 404000–405000, 405000–406000. There are 679 byte-pattern hits, but none contains a plausible direct-map kernel pointer in the following vm_next/vm_prev/tree/mm fields, even without alignment filtering. No surviving collector VMA or private COW mapping was validated. Evidence and scanner: stale_vma_swap_hits.json and stale_vma_swap.py. This does not prove that every historical VMA is absent.
3. **Compressed swap state:** boot logs show zswap initialized an lzo/zbud pool. However, the actual zswap.enabled kernel parameter is disabled: name VA ffffffff8c43af40 points to the literal zswap.enabled, parameter record at RAM-file2fc31a40 has ops ffffffff8c43af60, permission0644, and arg ffffffff8dd1af88. Kernel root1294000 translates the arg to physical3111af88, RAM-file310b7fc8, whose bool byte is00. The kernel_param layout was checked against official Linux v5.14 include/linux/moduleparam.h. Evidence: zswap_enabled_parameter.json.
4. **Swap usage:** six captured /proc/swaps buffers list only /dev/dm-1, size2117628KiB, Used0, priority-2. Boot logs identify /dev/mapper/cs-swap. No zram swap device appears. Other zram hits are static SELinux/device-name metadata. These are captured buffer states, not a timestamped guarantee about every prior instant. Evidence: code_route_audit_summary.json.

## What can be said about password formation

The original password formula remains unproved. The imports permit reading a hostname and a line of file data, formatting output, and generating pseudorandom bytes, but imports alone do not establish the input file, formatting string, ordering, hashing, or password length. The verified rand sequence explains the ZIP encryption headers; it does not by itself prove that rand generates the password. No new original code, rodata, call site, password bytes, or validated password was recovered in this pass.

Official source used for the parameter layout: https://raw.githubusercontent.com/torvalds/linux/v5.14/include/linux/moduleparam.h ; zswap initialization behavior: https://raw.githubusercontent.com/torvalds/linux/v5.14/mm/zswap.c .
