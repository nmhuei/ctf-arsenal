# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e
FROM rust:1.96-bookworm@sha256:a339861ae23e9abb272cea45dfafde21760d2ce6577a70f8a926153677902663 AS builder
ARG SFEX_GIT_REV=d9f6677e156304ee52b71eb31367309522b7f67e
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY sfex-Cargo.lock /sfex-lang/Cargo.lock
COPY runner ./runner
COPY app/Cargo.toml ./app/Cargo.toml
RUN mkdir -p app/src \
    && printf 'fn main() {}' > app/src/main.rs \
    && git init /sfex-lang \
    && git -C /sfex-lang remote add origin https://github.com/roriau0422/sfex-lang.git \
    && git -C /sfex-lang fetch --depth=1 origin "${SFEX_GIT_REV}" \
    && git -C /sfex-lang checkout --detach FETCH_HEAD \
    && test "$(git -C /sfex-lang rev-parse HEAD)" = "${SFEX_GIT_REV}" \
    && cargo build --locked --release --manifest-path /sfex-lang/Cargo.toml --bin sfex \
    && cargo build --locked --release --package sfex-playground-runner

FROM ubuntu:24.04@sha256:4fbb8e6a8395de5a7550b33509421a2bafbc0aab6c06ba2cef9ebffbc7092d90 AS rootfs
RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/* \
    && install -d /app
COPY --from=builder --chmod=0555 /sfex-lang/target/release/sfex /usr/local/bin/sfex
COPY --from=builder --chmod=0555 /build/target/release/runner /app/run
COPY --from=builder --chmod=0555 /build/target/release/flag /flag
RUN /usr/local/bin/sfex version

FROM rootfs
EXPOSE 5000
ENTRYPOINT ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:/app/run"]
