run
mount-ro /dev/sda3 /
sh "echo UNALLOC_USED_UNLINKED; ils -A -Z -L /dev/sda3 2>/dev/null | head -n 120; echo COUNT; ils -A -Z -L /dev/sda3 2>/dev/null | wc -l; echo ORPHANS; ils -p /dev/sda3 2>/dev/null | head -n 120; echo ORPHAN_COUNT; ils -p /dev/sda3 2>/dev/null | wc -l"
