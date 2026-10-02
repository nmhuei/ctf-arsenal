FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates fonts-liberation \
      libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
      libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
      libgbm1 libasound2t64 libpango-1.0-0 libcairo2 libatspi2.0-0t64 \
      libx11-6 libxcb1 libxext6 libxi6 libxtst6 libglib2.0-0t64 \
      python3 socat \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1337 ctf

ARG FLAG='SVATTT{local_testing_flag_replace_me}'
RUN printf '%s\n' "$FLAG" > /flag \
 && chown ctf:ctf /flag && chmod 600 /flag

RUN mkdir -p /etc/chromium/policies/managed /etc/opt/chrome/policies/managed
COPY deploy/policy.json /etc/chromium/policies/managed/policy.json
COPY deploy/policy.json /etc/opt/chrome/policies/managed/policy.json

COPY chrome /home/ctf/chrome
COPY deploy/bot.py /home/ctf/bot.py
RUN chmod -R a+rX /home/ctf/chrome && chmod 755 /home/ctf /home/ctf/bot.py

USER ctf
WORKDIR /home/ctf
EXPOSE 1337
CMD ["socat", "-T", "70", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 /home/ctf/bot.py'"]
