FROM python:3.14.6-slim-trixie@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061 AS app

RUN pip install --no-cache-dir mojo==1.0.0b2

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 🔥.py /srv/app/run
COPY --chmod=444 flag.txt /srv/app/flag.txt

RUN mv /srv/app/flag.txt /srv/flag-$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt \
 && rm -rf /srv/opt/modular \
 && ln -s /tmp /srv/opt/modular
ENV JAIL_MEM=300M JAIL_PIDS=30 JAIL_CPU=300 JAIL_TIME=120 JAIL_CONNS_PER_IP=2 JAIL_TMP_SIZE=1M
