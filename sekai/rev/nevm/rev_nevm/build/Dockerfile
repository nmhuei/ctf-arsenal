FROM rust:1-bookworm AS builder
WORKDIR /build
RUN mkdir revm-smc && cd revm-smc \
 && for c in revm-14.0.3 revm-interpreter-10.0.3 revm-primitives-10.0.0; do \
      curl -sSL "https://static.crates.io/crates/${c%-*}/$c.crate" | tar xz; \
    done \
 && mv revm-14.0.3 revm \
 && mv revm-interpreter-10.0.3 interpreter \
 && mv revm-primitives-10.0.0 primitives
COPY revm-smc.patch ./revm-smc.patch
RUN git apply -p1 --directory=revm-smc/interpreter revm-smc.patch
COPY runner/ ./runner/
RUN cd runner && cargo build --release --locked \
 && cp target/release/nevm-runner /nevm-runner

FROM debian:bookworm-slim
COPY --from=builder /nevm-runner /usr/local/bin/nevm-runner
WORKDIR /nevm
ENTRYPOINT ["nevm-runner"]
