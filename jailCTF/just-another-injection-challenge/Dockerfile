FROM python:3.14.6-slim-trixie@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061 AS app

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/jqlang/jq/releases/download/jq-1.8.2/jq-linux-amd64 -o /usr/bin/jq && \
    chmod +x /usr/bin/jq

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 server.py /srv/app/run

ENV JAIL_MEM=30M JAIL_TIME=240 JAIL_CONNS_PER_IP=2
