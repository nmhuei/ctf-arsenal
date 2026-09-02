FROM python:3.12.13-slim-trixie@sha256:6c4dd321d176d61ea848dc8c73a4f7dbae8f70e0ee48bb411ea2f045b599fa8e AS app
RUN pip install picklescan==1.0.5 fickling==0.1.12 modelscan==0.8.8

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 main.py /srv/app/run
COPY --chmod=444 flag.txt /srv/app/flag.txt

RUN mv /srv/app/flag.txt /srv/flag-$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt
ENV JAIL_MEM=80M JAIL_PIDS=30 JAIL_TIME=60 JAIL_TMP_SIZE=1M JAIL_CONNS_PER_IP=2
