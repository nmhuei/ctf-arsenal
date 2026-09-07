FROM python:3.12-slim
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/*

COPY chall.py /app/chall.py

ENV FLAG="TEST{mid_local_flag}"
EXPOSE 1338

# socat forks a new chall.py per connection, binds on 1338
CMD ["socat", "TCP-LISTEN:1338,reuseaddr,fork", "EXEC:python3 -u /app/chall.py"]
