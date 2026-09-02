FROM ubuntu:24.04@sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54 AS app
RUN apt update --yes && apt upgrade --yes
RUN apt install python3 nodejs --yes

# the install+build process for haskell stuff is so complex and lengthy that it would be sadistic to put it inside the dockerfile
# anyways the project is located at https://github.com/kbmackenzie/mewlix/
# just know that the binary is directly generated from source code of commit 9e63f36e015c52c30c2e6ba9d0512a96ef245be4

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 mewlix /srv/app/mewlix
COPY --chmod=755 mewlix-files /srv/app/mewlix-files
COPY --chmod=755 main.py /srv/app/run
COPY --chmod=444 flag.txt /srv/app/flag.txt

RUN mv /srv/app/flag.txt /srv/flag-$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32).txt
ENV JAIL_MEM=50M JAIL_PIDS=30 JAIL_TIME=40 JAIL_CONNS_PER_IP=2 JAIL_TMP_SIZE=1M
