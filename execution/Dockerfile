FROM rust:1.75 AS builder
WORKDIR /app
COPY Cargo.toml build.rs ./
COPY proto ./proto
RUN mkdir src && echo 'fn main() {}' > src/main.rs && cargo build --release || true
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/aion-execution ./aion-execution
EXPOSE 50051
CMD ["./aion-execution"]
