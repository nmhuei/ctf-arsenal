FROM node:22-bookworm-slim

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx supervisor ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY apps/backstage1/package.json ./apps/backstage1/package.json
COPY apps/backstage2/package.json ./apps/backstage2/package.json

RUN cd apps/backstage1 \
  && npm install --no-audit --no-fund --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000
RUN cd apps/backstage2 \
  && npm install --no-audit --no-fund --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

COPY apps ./apps
COPY public ./public

RUN cd apps/backstage1 && npm run build
RUN cd apps/backstage2 && npm run build

COPY flag.txt /flag.txt
COPY config/nginx-main.conf /etc/nginx/nginx.conf
COPY config/nginx.conf /etc/nginx/conf.d/default.conf
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN rm -f /etc/nginx/sites-enabled/default \
  && mkdir -p /tmp/nginx/client_body /tmp/nginx/proxy /tmp/nginx/fastcgi /tmp/nginx/uwsgi /tmp/nginx/scgi \
  && chown -R node:node /app /tmp/nginx

USER node

EXPOSE 8080 8081
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
