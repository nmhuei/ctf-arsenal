run
mount-ro /dev/sda3 /
sh "parted -s /dev/sda unit B print"
