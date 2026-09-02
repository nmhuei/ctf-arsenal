run
mount-ro /dev/sda3 /
echo "=== bash_history ==="
cat /root/.bash_history
echo "=== zsh_history ==="
cat /root/.zsh_history
echo "=== generic history ==="
cat /root/.history
echo "=== python history ==="
cat /root/.python_history
echo "=== viminfo strings ==="
sh "strings /sysroot/root/.viminfo 2>/dev/null | tail -n 300"
