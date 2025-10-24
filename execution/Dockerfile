FROM rust:1.77 as builder
WORKDIR /app
COPY Cargo.toml build.rs ./
COPY proto ./proto
RUN cargo fetch
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/aion-execution ./aion-execution
EXPOSE 50051
CMD ["./aion-execution"]
