#!/bin/sh
head -n 1 > /tmp/code.glass
stdbuf -o0 -e0 ./glass /tmp/code.glass
