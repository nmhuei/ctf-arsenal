FROM ubuntu:noble@sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54 AS app

WORKDIR /app/
RUN apt update --yes
RUN apt install git=1:2.43.0-1ubuntu7.3 make=4.3-4.1build2 gcc=4:13.2.0-7ubuntu1 --yes

RUN git clone https://github.com/python/cpython
WORKDIR /app/cpython/
RUN git checkout b0689ae7f9d904bc2126994aedbc552f03479e40
RUN echo "*static*" >> Modules/Setup.local
RUN echo "_pickle _pickle.c" >> Modules/Setup.local
RUN echo "_struct _struct.c" >> Modules/Setup.local
RUN ./configure LDFLAGS="-static" --disable-shared
RUN make LDFLAGS="-static" LINKFORSHARED=" "

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=444 flag.txt /srv/app/flag.txt
COPY --chmod=755 my_first_unpickler.py /srv/app/run

RUN mv /srv/app/flag.txt /srv/flag-$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt
ENV JAIL_MEM=60M JAIL_PIDS=30 JAIL_TIME=30 JAIL_CONNS_PER_IP=2

