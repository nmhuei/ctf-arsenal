#!/bin/sh
set -eu

[ -e /dev/kmsg ] || mknod /dev/kmsg c 1 11

if [ -e /sys/fs/cgroup/cgroup.controllers ] && grep -qx "$$" /sys/fs/cgroup/cgroup.procs 2>/dev/null; then
	mkdir -p /sys/fs/cgroup/init
	for pid in $(cat /sys/fs/cgroup/cgroup.procs); do
		echo "$pid" >/sys/fs/cgroup/init/cgroup.procs 2>/dev/null || true
	done
	sed -e 's/ / +/g' -e 's/^/+/' </sys/fs/cgroup/cgroup.controllers >/sys/fs/cgroup/cgroup.subtree_control
fi

exec /usr/local/bin/supervisord -c /etc/supervisord.conf
