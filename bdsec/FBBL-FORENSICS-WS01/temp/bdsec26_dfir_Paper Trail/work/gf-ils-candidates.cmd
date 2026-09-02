run
mount-ro /dev/sda3 /
sh "ils -A -Z -L /dev/sda3 2>/dev/null | awk -F'|' 'NR>3 && \$11>0 && \$11<20000000 {print}' | tail -n 2000"
