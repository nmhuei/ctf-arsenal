FROM node:lts-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./

RUN curl -LsSf https://github.com/ton-blockchain/acton/releases/latest/download/acton-installer.sh | sh

ENV PATH="/root/.acton/bin:${PATH}"
RUN acton up 1.0.0

COPY . .

RUN npm install
RUN npm run build
RUN npm run wrappers-ts

EXPOSE 1337
EXPOSE 3000

CMD ["npm", "run", "server"]
