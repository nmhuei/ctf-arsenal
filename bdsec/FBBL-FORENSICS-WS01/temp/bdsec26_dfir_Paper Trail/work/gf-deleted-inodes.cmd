run
mount-ro /dev/sda3 /
sh "echo DEBUGFS_LSDEL; debugfs -R lsdel /dev/sda3 2>/dev/null | head -n 80; echo TSK_ILS_HEAD; ils -e /dev/sda3 2>/dev/null | head -n 80; echo COUNTS; debugfs -R lsdel /dev/sda3 2>/dev/null | wc -l; ils -e /dev/sda3 2>/dev/null | wc -l"
