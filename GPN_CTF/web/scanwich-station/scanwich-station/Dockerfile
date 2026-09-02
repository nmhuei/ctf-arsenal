FROM ubuntu:24.04@sha256:db6914f1ac0c566f57857641e2214e3f3e453cb340cc2c890ed6c2b7b81b8a00 AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends clang libc6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY src ./src
COPY vendor ./vendor

RUN mkdir -p /out && \
    clang -O2 -DNDEBUG -Ivendor/quirc/lib -D_FORTIFY_SOURCE=3 \
      -fPIE -fstack-protector-all \
      -fstack-clash-protection -fcf-protection=full -ftrivial-auto-var-init=zero \
      -Wall -Wextra -Wpedantic \
      src/qrscan.c \
      vendor/quirc/lib/quirc.c vendor/quirc/lib/decode.c \
      vendor/quirc/lib/identify.c vendor/quirc/lib/version_db.c \
      -pie -Wl,-z,relro -Wl,-z,noexecstack -Wl,-z,separate-code -s \
      -o /out/qrscan -lm && \
    clang -O2 -DNDEBUG -D_FORTIFY_SOURCE=3 \
      -fPIE -fstack-protector-all \
      -fstack-clash-protection -fcf-protection=full -ftrivial-auto-var-init=zero \
      -Wall -Wextra -Wpedantic \
      src/read_flag.c \
      -pie -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -Wl,-z,separate-code -s \
      -o /out/read_flag

# Don't change the stage name
FROM scratch AS handout

COPY Dockerfile /handout/
COPY app /handout/app
COPY src /handout/src
COPY vendor /handout/vendor
CMD ["/handout"]

# Don't change the stage name
FROM ubuntu:24.04@sha256:db6914f1ac0c566f57857641e2214e3f3e453cb340cc2c890ed6c2b7b81b8a00 AS challenge

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-flask python3-pil python3-png python3-pyzbar util-linux && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1337 ctf

WORKDIR /challenge
RUN mkdir -p dist /run/chal && \
    cp /lib64/ld-linux-x86-64.so.2 /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libm.so.6 dist/
COPY --from=builder /out/qrscan dist/qrscan
COPY --from=builder /out/read_flag /read_flag
COPY app ./app

ARG FLAG=GPNCTF{test_flag}
RUN echo "$FLAG" > /flag && \
    chmod 0555 ./dist/qrscan ./dist/ld-linux-x86-64.so.2 && \
    chmod 0444 ./dist/libc.so.6 ./dist/libm.so.6 && \
    chown root:root /flag /read_flag && \
    chmod 4555 /read_flag && \
    chmod 000 /flag

VOLUME ["/run/chal"]
EXPOSE 5000

CMD ["/bin/sh", "-c", "cp /challenge/dist/* /run/chal/ && exec setpriv --reuid=1337 --regid=1337 --init-groups python3 /challenge/app/app.py"]
