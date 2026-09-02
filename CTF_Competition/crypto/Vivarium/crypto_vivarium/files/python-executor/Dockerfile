FROM ghcr.io/astral-sh/uv:0.12.0@sha256:606e70c71c852d03f611b1e56a195d08648507018a7057fab82c4974c4eae105 AS python-builder
WORKDIR /tmp
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_BIN_DIR=/python/bin
ENV UV_LIBC=gnu
RUN ["/uv", "python", "install", "3.13", "--default", "--no-cache"]

FROM rust:1.96-bookworm@sha256:a339861ae23e9abb272cea45dfafde21760d2ce6577a70f8a926153677902663 AS builder

WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY sandbox ./sandbox
COPY src ./src
RUN cargo build --locked --release --bin python-executor
RUN rustc -O -C target-feature=+crt-static -C strip=symbols src/bin/flag.rs -o /flag

FROM gcr.io/distroless/cc-debian12:latest@sha256:e8e7ee4b8b106d4c5fde9e422a321b2b8a2d5cca546c97adcce927f3e1d36e36

COPY --from=builder /build/target/release/python-executor /app/python-executor
COPY --from=builder --chmod=0555 /flag /flag
COPY --from=python-builder /python /python
ENV PYTHON_BIN=/python/bin/python3

EXPOSE 8081
ENTRYPOINT ["/app/python-executor"]
