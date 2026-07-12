FROM rust:1.85-bookworm AS builder

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*
COPY schemas/v1/protos ./schemas/v1/protos
COPY runtime-daemon ./runtime-daemon
WORKDIR /app/runtime-daemon
RUN cargo build --release

FROM debian:bookworm-slim

RUN useradd --system --uid 10001 --create-home runtime
COPY --from=builder /app/runtime-daemon/target/release/runtime-daemon /usr/local/bin/runtime-daemon

USER runtime
EXPOSE 50051
ENTRYPOINT ["/usr/local/bin/runtime-daemon"]
