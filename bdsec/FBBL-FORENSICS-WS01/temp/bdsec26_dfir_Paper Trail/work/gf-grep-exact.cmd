run
mount-ro /dev/sda3 /
sh "for q in transfer_receipt_may10.pdf 'external bank account' 'bank account ID' 'Rajesh Patel' 'Aman Reza' 'A. Reza' 'RPC Consulting'; do echo QUERY:$q; grep -aob -F -m 50 \"$q\" /dev/sda3 2>/dev/null; done"
