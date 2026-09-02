#!/usr/bin/env sh
set -eu
here=$(cd "$(dirname "$0")" && pwd)
img=${NEVM_IMAGE:-nevm}
docker image inspect "$img" >/dev/null 2>&1 || docker build -t "$img" "$here/build"
exec docker run --rm -v "$here:/nevm:ro" -w /nevm "$img" "$@"
