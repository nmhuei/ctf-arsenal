#!/bin/sh
set -eu

: "${FLAG:?FLAG must be set}"

node -e '
const fs = require("node:fs");
const src = fs.readFileSync("/src/readflag.c", "utf8");
const flag = JSON.stringify(process.env.FLAG).slice(1, -1);
// function replacement: the flag may contain $ or ` which are special in a string replacement
fs.writeFileSync("/tmp/readflag.c", src.replace("NNS{REPLACE_ME}", () => flag));
'
gcc /tmp/readflag.c -static -O2 -s -o /tmp/readflag
cat /tmp/readflag > /readflag
chmod 0111 /readflag
rm -f /tmp/readflag /tmp/readflag.c

unset FLAG
exec socat tcp-l:1337,reuseaddr,fork EXEC:"node --disallow-code-generation-from-strings /home/jail/chal.js"
