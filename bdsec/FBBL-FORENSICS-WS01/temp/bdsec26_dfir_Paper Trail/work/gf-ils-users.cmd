run
mount-ro /dev/sda3 /
sh "ils -A -Z -L /dev/sda3 2>/dev/null | grep -E '\\|(1001|1002|1003|1004)\\|' | tail -n 2000"
