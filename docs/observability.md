# Observability Stack

- Prometheus scrapes the control plane metrics endpoint (`/metrics`) and gateway metrics when exposed.
- Grafana provisioning files auto-register a Prometheus datasource and dashboard.
- Extend tracing by enabling OpenTelemetry exporters in FastAPI (`structlog` integration ready).
- Execution plane exposes logs via `tracing_subscriber`; forward to Loki by running the binary with `RUST_LOG` configured.
