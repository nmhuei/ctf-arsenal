FROM node:20-slim

# nginx fronts the app on the public port; the Node app binds loopback only.
RUN apt-get update \
 && apt-get install -y --no-install-recommends nginx \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY src/ ./src/
COPY nginx.conf ./nginx.conf
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Let the unprivileged user write nginx runtime files.
RUN mkdir -p /var/lib/nginx /var/log/nginx /tmp/nginx-client-body \
 && chown -R node:node /var/lib/nginx /var/log/nginx /app

ENV FLAG="TFC{set-the-FLAG-environment-variable}"
ENV PORT=8001
ENV BIND_ADDR=127.0.0.1

# Public port stays 3000 (nginx). The app is internal-only on 127.0.0.1:8001.
EXPOSE 3000
USER node
CMD ["./entrypoint.sh"]
