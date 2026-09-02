run
mount-ro /dev/sda3 /
sh "find /home/arif.khan /home/salim.uddin /home/it.admin /home/tania.akter /root -xdev -type f -printf '%p\t%s\n' 2>/dev/null | grep -Evi '/(cache|Cache|__pycache__|node_modules|Trash|thumbnails|fontconfig|mesa_shader_cache)/' | sort"
