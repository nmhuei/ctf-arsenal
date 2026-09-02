FROM python:3.14.2 AS app

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 chal.py /srv/app/run
COPY --chmod=444 flag.txt /srv/app/flag.txt

ENV JAIL_MEM=50M JAIL_TIME=60 JAIL_CONNS_PER_IP=2
