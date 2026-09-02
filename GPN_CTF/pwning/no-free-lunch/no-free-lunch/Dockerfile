FROM debian:13 AS builder
RUN apt-get update && apt-get install -y \
    build-essential git clang \
    && rm -rf /var/lib/apt/lists/*

ENV CC=clang CXX=clang++

WORKDIR /cpython
RUN git init && git remote add origin https://github.com/python/cpython.git && \
    git fetch --depth 1 origin c62c3710dc795a60c3c3dc8e2aeeeb16c06da197 && git checkout FETCH_HEAD
ADD src/Setup.local /cpython/Modules/
ADD src/*.patch /cpython/
RUN git apply *.patch
RUN ./configure && make -j$(nproc)
# The make install fails because of the patch, but we don't actually need it to succeed.
RUN make install || python3 --version

#-----------------------------------------

FROM debian:13 AS flag-reader
RUN apt-get update && apt-get install -y gcc \
    && apt-get clean
COPY src/read_flag.c .
RUN gcc -o /read_flag read_flag.c

#-----------------------------------------

# Don't change the stage name
FROM debian:13 AS handout
COPY --from=builder /cpython/python /handout/src/python
COPY --from=builder /cpython/Lib/heapq.py /handout/src/lib/heapq.py
COPY --from=builder /cpython/Modules/_heapq*.so /handout/src/lib/

RUN cp /lib/x86_64-linux-gnu/libc.so.6 /handout/libc.so.6
RUN cp /lib/x86_64-linux-gnu/libm.so.6 /handout/libm.so.6
RUN cp /lib64/ld-linux-x86-64.so.2 /handout/ld-linux-x86-64.so.2

COPY --chmod=555 src/server.py /handout/src/server.py

COPY src/*.patch /handout/src/
COPY src/Setup.local /handout/src/
COPY src/read_flag.c /handout/src/read_flag.c

COPY Dockerfile /handout/

#-----------------------------------------

# Don't change the stage name
FROM debian:13 AS challenge
EXPOSE 1337

RUN apt-get update && apt-get install -y \
    python3 socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge
COPY --from=builder /cpython/python python
COPY --from=builder /cpython/Lib/heapq.py lib/heapq.py
COPY --from=builder /cpython/Modules/_heapq*.so lib/
COPY --from=flag-reader /read_flag .

ARG FLAG=GPNCTF{fake_flag}
RUN echo "$FLAG" > /flag
RUN chmod u+s read_flag && \
    chmod 700 /flag

ADD src/server.py /challenge/

RUN useradd -m ctf
USER ctf
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/usr/bin/stdbuf -i0 -o0 -e0 python3 /challenge/server.py,stderr"]
