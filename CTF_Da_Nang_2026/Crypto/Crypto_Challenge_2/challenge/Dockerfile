FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -d /home/app -s /usr/sbin/nologin app

WORKDIR /opt/chall
COPY server/server.py /opt/chall/server.py
COPY wrapper.sh /opt/chall/wrapper.sh
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN pip install --no-cache-dir numpy==1.26.4 \
    && chmod 0755 /opt/chall/server.py /opt/chall/wrapper.sh /usr/local/bin/docker-entrypoint.sh \
    && chown -R root:root /opt/chall

EXPOSE 9999
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
