FROM rust:1.96-bookworm@sha256:a339861ae23e9abb272cea45dfafde21760d2ce6577a70f8a926153677902663 AS flag-builder

WORKDIR /src
COPY flag/Cargo.toml flag/Cargo.lock ./
COPY flag/src ./src
RUN cargo build --locked --release \
        --bin my-avatar-flag \
        --bin my-avatar-flag-service \
    && cp target/release/my-avatar-flag /flag \
    && cp target/release/my-avatar-flag-service /flag-service \
    && strip /flag /flag-service

FROM debian:bookworm-slim@sha256:7b140f374b289a7c2befc338f42ebe6441b7ea838a042bbd5acbfca6ec875818 AS flag-service

COPY --from=flag-builder /flag-service /usr/local/bin/flag-service

ENTRYPOINT ["/usr/local/bin/flag-service"]

FROM php:8.3-fpm@sha256:32b6cb4cf9f41d3e62424e64959bbf824125ca7b7869c18fb54d4bafc9d990b4 AS php-runtime

ARG DEBIAN_SNAPSHOT=20260713T000000Z

RUN sed -i \
        -e "s|http://deb.debian.org/debian-security|http://snapshot.debian.org/archive/debian-security/${DEBIAN_SNAPSHOT}|" \
        -e "s|http://deb.debian.org/debian|http://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT}|" \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends \
        libfreetype-dev=2.13.3+dfsg-1+deb13u1 \
        libavif-dev=1.2.1-1.2 \
        libjpeg62-turbo-dev=1:2.1.5-4 \
        libpng-dev=1.6.48-1+deb13u5 \
        libsqlite3-dev=3.46.1-7+deb13u1 \
        libwebp-dev=1.5.0-0.1 \
    && docker-php-ext-configure gd --with-avif --with-freetype --with-jpeg --with-webp \
    && docker-php-ext-install -j"$(nproc)" gd pdo_sqlite \
    && rm -rf /var/lib/apt/lists/*

FROM php-runtime AS avatar-validator-builder

COPY validator/avatar-validator.c /src/avatar-validator.c

RUN cc -std=c11 -O2 -Wall -Wextra -Werror \
        /src/avatar-validator.c -lavif -o /avatar-validator \
    && strip /avatar-validator

FROM php-runtime

COPY --from=flag-builder --chmod=0755 /flag /flag
COPY --from=avatar-validator-builder /avatar-validator /usr/local/bin/avatar-validator

WORKDIR /var/www/html

COPY web/ ./
COPY php-fpm.conf /usr/local/etc/php-fpm.d/zz-my-avatar.conf

RUN mkdir -p data public/uploads public/avatars /run/php \
    && chown -R www-data:www-data data public/uploads public/avatars /run/php

VOLUME ["/var/www/html/public/avatars", "/run/php", "/run/my-avatar-flag"]

CMD ["php-fpm", "-F"]
