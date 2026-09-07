FROM python:3.15-rc-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY jail.py /app/jail.py
RUN printf '%s\n' 'TEST{flag}' > /flag.txt \
    && chmod 400 /flag.txt
CMD ["python3", "-u", "/app/jail.py"]
