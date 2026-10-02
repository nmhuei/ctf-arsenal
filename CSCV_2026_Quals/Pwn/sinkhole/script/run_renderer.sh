#!/bin/bash
gdb -batch -x script/gdb_renderer.txt --args "$@" > /tmp/gdb_out.log 2>&1
