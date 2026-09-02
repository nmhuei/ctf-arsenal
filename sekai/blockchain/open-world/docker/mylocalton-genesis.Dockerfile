ARG MLT_IMAGE=ghcr.io/neodix42/mylocalton-docker
ARG TON_BRANCH=latest

FROM ${MLT_IMAGE}:${TON_BRANCH}

COPY --chmod=755 docker/update-wallet.sh /scripts/update-wallet.sh