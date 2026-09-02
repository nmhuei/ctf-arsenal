# syntax=docker/dockerfile:1

FROM rust:1.96-bookworm@sha256:a339861ae23e9abb272cea45dfafde21760d2ce6577a70f8a926153677902663 AS builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY web ./web
RUN cargo build --locked --release

FROM gcr.io/distroless/cc-debian12:latest@sha256:e8e7ee4b8b106d4c5fde9e422a321b2b8a2d5cca546c97adcce927f3e1d36e36
COPY --from=builder /build/target/release/vivarium-frontend /app/frontend
ENV EXECUTOR_URL=http://python-executor:8081/api/run
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/app/frontend"]
