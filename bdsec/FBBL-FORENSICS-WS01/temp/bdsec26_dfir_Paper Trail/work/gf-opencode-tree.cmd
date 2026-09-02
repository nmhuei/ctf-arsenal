run
mount-ro /dev/sda3 /
echo "=== OPENCODE CONFIG ==="
find /home/investigator/.config/opencode
echo "=== OPENCODE DATA ==="
find /home/investigator/.local/share/opencode
echo "=== OPENCODE CACHE ==="
find /home/investigator/.cache/opencode
