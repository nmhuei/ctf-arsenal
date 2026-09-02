run
mount-ro /dev/sda3 /
sh "grep -aob -F 'transfer_receipt_may10.pdf' /dev/sda3 2>/dev/null | head -n 100"
