FROM ubuntu:focal-20250404@sha256:8feb4d8ca5354def3d8fce243717141ce31e2c428701f6682bd2fafe15388214 AS app

RUN mkdir /app
RUN apt update && apt -y upgrade
RUN apt install -y wget build-essential
RUN wget https://github.com/graue/esofiles/raw/master/glass/impl/glass-0.12.tar.bz2 -O /tmp/glass.tar.bz2
RUN tar -xf /tmp/glass.tar.bz2 -C /tmp
WORKDIR /tmp/glass-0.12
RUN make -j$(nproc) CXXFLAGS="-O2 -g -include stdio.h -include string.h -fno-pie -no-pie"
RUN cp /tmp/glass-0.12/glass /app/glass

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 run.sh /srv/app/run
COPY --chmod=444 flag.txt /srv/app/flag.txt

RUN mv /srv/app/flag.txt /srv/flag-$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt
ENV JAIL_TIME=60 JAIL_CONNS_PER_IP=2 JAIL_TMP_SIZE=1M
