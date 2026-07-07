mod config;
mod execution {
    pub mod agent_runner;
    pub mod command;
}
mod isolation {
    pub mod cpu;
    pub mod gpu;
    pub mod memory;
}
mod observability {
    pub mod metrics;
}
mod sandbox {
    pub mod mount;
    pub mod namespace;
    pub mod process;
    pub mod seccomp;
}
mod security {
    pub mod capability;
}
mod server;

use config::RuntimeConfig;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    if std::env::args().any(|arg| arg == "--healthcheck") {
        let address = std::env::var("AION_RUNTIME_HEALTH_ADDR")
            .unwrap_or_else(|_| "127.0.0.1:50051".to_string());
        tokio::net::TcpStream::connect(address).await?;
        return Ok(());
    }

    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    let config = RuntimeConfig::default();
    tracing::info!(bind_addr = %config.bind_addr, profile = %config.profile, "runtime daemon starting");
    server::run_server(config).await
}
