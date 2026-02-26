mod cluster {
    pub mod node_registration;
    pub mod resource_report;
}
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
    pub mod logging;
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
    pub mod signature;
}
mod server;

use config::RuntimeConfig;
use observability::logging::init_logging;
use server::run_server;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    init_logging();
    run_server(RuntimeConfig::default()).await
}
