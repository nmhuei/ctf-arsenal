FROM gcc:16.1.0 AS builder
WORKDIR /opt
COPY readflag.c flag.txt .
RUN gcc -std=c23 -O2 -s -static -o readflag readflag.c

FROM python:3.14.6-slim-trixie@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061 AS app
COPY main.py /app/run
COPY --from=builder /opt/readflag /readflag

RUN chmod 755 /app/run && \
    chmod 111 /readflag

FROM pwn.red/jail
COPY --from=app / /srv

ENV JAIL_MEM=32M JAIL_TIME=60 JAIL_CONNS_PER_IP=2
