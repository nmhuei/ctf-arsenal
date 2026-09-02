FROM node:22-alpine AS base

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN corepack enable

WORKDIR /app

FROM base AS dependencies

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM dependencies AS build

COPY index.html tsconfig.json tsconfig.server.json vite.config.ts ./
COPY src ./src
RUN pnpm build

FROM base AS production-dependencies

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --prod --frozen-lockfile

FROM gcr.io/distroless/nodejs22-debian12:nonroot AS runtime

ENV NODE_ENV=production
ENV PORT=3000

WORKDIR /app

COPY --from=production-dependencies --chown=65532:65532 /app/node_modules ./node_modules
COPY --from=build --chown=65532:65532 /app/dist ./dist
COPY --from=build --chown=65532:65532 /app/server-dist ./server-dist
COPY --chown=65532:65532 package.json ./package.json

USER 65532:65532

EXPOSE 3000

CMD ["server-dist/server.js"]
