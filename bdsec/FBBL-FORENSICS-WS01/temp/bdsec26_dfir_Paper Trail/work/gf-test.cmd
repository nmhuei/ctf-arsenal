run
mount-ro /dev/sda3 /
sh "command -v debugfs || true; command -v fls || true; uname -a; ls -l /dev/sda3"
