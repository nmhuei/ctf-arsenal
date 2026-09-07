#!/bin/bash

docker build -t python-jail .
docker run --rm --cap-add=SYS_PTRACE -p 1234:1234 python-jail