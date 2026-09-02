run
mount-ro /dev/sda3 /
sh "echo TARGETED; fls -r -d -p /dev/sda3 2>/dev/null | grep -Eai 'account|bank|payment|transfer|receipt|invoice|beneficiary|wire|raj|reza|rpc|consult|fee|instruction|secure|wallet|statement' | head -n 500; echo HOMES; fls -r -d -p /dev/sda3 2>/dev/null | grep -Ea 'home/(arif.khan|salim.uddin|it.admin|tania.akter)/' | head -n 800"
