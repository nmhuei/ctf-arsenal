#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
build_dir="${LADYBIRD_JS_ONLY_BUILD_DIR:-${root}/Build/js-only}"

python3 "${root}/Meta/Utils/build_vcpkg.py"

cmake -S "${root}/Meta/JSOnly" \
    -B "${build_dir}" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_TOOLCHAIN_FILE="${root}/Build/vcpkg/scripts/buildsystems/vcpkg.cmake" \
    "$@"

cmake --build "${build_dir}" --target js
