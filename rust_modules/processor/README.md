# Processor Rust Module

This binary receives a JSON payload on stdin, performs lightweight text processing, and emits a JSON response. It demonstrates how AgentOS can offload latency-sensitive preprocessing work to a memory-safe executable.

## Running locally

```bash
cd rust_modules/processor
cargo run --quiet <<'JSON'
{"operation":"summarize","text":"Example text."}
JSON
```
