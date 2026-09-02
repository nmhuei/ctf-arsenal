#!/bin/sh
set -eu

: "${FLAG:=flag{local_dev_dynamic_flag_placeholder}}"
export FLAG

exec /opt/chall/wrapper.sh
