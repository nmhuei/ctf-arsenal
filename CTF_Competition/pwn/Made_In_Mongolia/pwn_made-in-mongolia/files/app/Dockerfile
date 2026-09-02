# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e
FROM rust:1.96-bookworm@sha256:a339861ae23e9abb272cea45dfafde21760d2ce6577a70f8a926153677902663 AS builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY app ./app
COPY runner/Cargo.toml ./runner/Cargo.toml
RUN mkdir -p runner/src/bin \
    && printf 'fn main() {}' > runner/src/main.rs \
    && printf 'fn main() {}' > runner/src/bin/flag.rs \
    && cargo build --locked --release --package sfex-playground-app

FROM debian:bookworm-slim@sha256:7b140f374b289a7c2befc338f42ebe6441b7ea838a042bbd5acbfca6ec875818
COPY --from=builder /build/target/release/sfex-playground-app /usr/local/bin/app

ENV HTTP_LISTEN_ADDRESS=0.0.0.0:3000 \
    RUNNER_ADDRESS=runner:5000
EXPOSE 3000
ENTRYPOINT ["/usr/local/bin/app"]
