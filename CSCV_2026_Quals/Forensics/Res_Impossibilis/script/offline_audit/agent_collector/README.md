# Collector and Firefox memory audit

No complete original collector executable or new complete profile file was recovered in this branch. `recovered_files/` remains empty. `candidate_*` files contain explicit zero gaps or stale data and must not be presented as recovered documents.

## Kernel translations recovered

`kernel_walk.py` reads validated LiME ranges and exposes `p2f(physical)`, `f2p(file_offset)`, `walk(root_physical, virtual)` and read-only mmap `m`. Root physical `0x1294000` translates the kernel direct map correctly. `kernel_roots.json` records 195 root candidates sharing that validated mapping; this is not a process count.

Constants: direct map `0xffff978e40000000`; vmemmap `0xffffe18300000000`; struct page size 64. Walk vmemmap through the page tables instead of assuming physical contiguity. `audit_roots.py` checked user addresses 0x400000..0x405000 in all roots: only two roots map a different executable there; no collector mapping was found.

## Acquisition includes its own dump cache

The collector inode xarray page pointers translate to the expected physical addresses, but their later-captured struct-page mapping fields point to `0xffff978f4c1d6ef8`. This is the address_space of inode `0xffff978f4c1d6d80`, whose alias dentry `0xffff979067c0a180` is named `mem.dmp`. Its recorded inode size is 3423875198; later page metadata has file indexes extending beyond this value. These data were acquired at different physical offsets and are inconsistent as a single instantaneous state. Acquisition memory smear is a plausible explanation; there is no evidence here proving deliberate memory wiping.

`validate_pages.py` / `page_validation.json` record physical addresses, translated struct-page addresses, mapping/index/refcounts and SHA256 for the seven relevant pages. A second collector header at file 0x2f6b7040 differs from the original first page only at bytes 0..15. No user PTE or adjacent executable pages were found for it.

`dump_cache.py` provides `xarray_lookup(file_page_index, head=0xffff978e81830922)` returning (physical_page, trace). For a source byte offset, use page index floor(offset/4096), then add offset%4096 to the returned physical page's file translation. The cached collector header at file0x3f96f080 exactly matches the source; cached text/rodata copies also match their original zero/near-zero contents. These verified cache copies do not recover the missing code.

`dump_cache_index.npy` records 822040 candidate pages from current struct-page mapping/index fields. Their payloads may have been captured before those assignments and must be independently validated. `cache_nodes.py` reconstructs 200913 cache entries by following xarray parent links, in `dump_cache_node_index.npy`; this covers source page indexes 0..920831. 1703 leaf nodes lacked consistent parent chains. Neither lookup reliably recovered missing high-offset archive pages.

## Original Firefox profile files

`profile_inodes.py` validates inline dentry name pointers and follows parents to `/tmp/firefox-clean`. `profile_inodes.json` records exact inode, mapping and xarray head evidence:

- extensions.json, 37583 bytes: pages 0..8 are xarray shadow entries; page9 survives at RAM-file0xea99d07e, physical0x12aa30000. Its struct-page mapping matches the original inode, index9. `extensions.json.tail.bin` contains the final719 bytes, original file offset36864.
- AlternateServices.txt, 5398 bytes: page0 pointer leads to a page now assigned to mem.dmp; it is not accepted. Page1 at RAM-file0x1da7e807e, physical0x21a87b000, maps the original inode at index1. `AlternateServices.txt.tail.bin` contains final1302 bytes, original offset4096.
- handlers.json, 683 bytes, CRC6df5e5fd: inodeffff978f8a89b960, mappingffff978f8a89bad8, headb52df0001001 (shadow only).
- SiteSecurityServiceState.txt,1043 bytes, CRCe16206f5: inodeffff978f8a8a04e0, mappingffff978f8a8a0658, headb589a0001001 (shadow only).

`profile_recovery.json` records all page traces and failed full CRCs. The archive agent independently used the extensions final719 bytes to decrypt the final2318 archived bytes; consult its separate artifacts for that validation.

Full-memory searches found no extra UTF8 copies of either tail prefix, no UTF16LE extensions JSON prefix (including a shorter schemaVersion signature), and no UTF16LE tail copies. All six matching AlternateServices records reside inside the known last page, even with the timestamp-independent :3-tab0-tab signature. The missing pages remain unrecovered.

All scans here using ripgrep omit --replace, so byte offsets are not affected by replacement-length shifts. No captured executable was run. All work remained offline.

## Bounded Firefox runtime follow-up

The specific Bing extension ID was absent in ASCII and UTF16LE. No mozLz40 header was present. Compressed profile files search.json.mozlz4 (180 bytes), addonStartup.json.lz4 (3932) and sessionstore.jsonlz4 (13032) have exact /tmp/firefox-clean dentries but zero xarray heads/nrpages. No nsSiteSecurityService or AltSvcMapping strings were found. All 20 libxul.so hits inspected were package metadata, not native-library runtime strings. This supplies no positive anchor for reconstructing live Firefox C++ network-state tables. It does not prove Firefox process absence: a generic task-comm heuristic also failed on control processes and was discarded.

Package metadata near file0x128d58ac2 identifies firefox-91.3.0-1.el9.src.rpm and version91.3.0-1.el9; exact string offsets are in firefox_package_version.json. This may identify the static search-engine definitions relevant to extensions.json. Profile timestamps are preserved separately in profile_timestamps.json. No new complete file or Bing GUID was recovered.

The profile dentry tree was then traversed directly (357 entries). Only 15 files have nonempty page-cache mappings, all JSON/TXT members selected by the collector; the other profile/cache files have empty mappings. Profile mtime/ctime values are 2026-09-08 04:07..04:28 UTC, whereas collected files have atime16:32:01UTC. This supports historical profile data accessed later by the collector, without proving an exact Firefox exit time. The XFS symlink for profile lock points to 127.0.0.1:+4144 (pointer at inode-0xc0); PID activity is unverified. profile_lock.json records its precise source.
