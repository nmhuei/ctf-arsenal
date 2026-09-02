FROM python:3.10.20-slim-trixie@sha256:c4015e4e509b1aae50f742d32798ab65b8d08863305f61da5a0b0072d0070348 AS app

FROM pwn.red/jail
COPY --from=app / /srv
COPY --chmod=755 main.py /srv/app/run
ENV JAIL_MEM=30M JAIL_TIME=25

