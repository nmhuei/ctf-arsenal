run
mount-ro /dev/sda3 /
sh "grep -aRIniE 'Rajesh Patel|A[.] Reza|Aman Reza|account[ _-]*(number|no|id)|bank[ _-]*account|beneficiary|routing|SWIFT|IFSC|wire instructions|payment instructions|external account|commission|consulting fee|remittance|settlement|payout' /home/arif.khan/snap/firefox/common/.cache/mozilla/firefox/390s6fqa.default/cache2 2>/dev/null | head -n 2000"
