use tokio::signal;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt().with_env_filter("info").init();
    tracing::info!("omertaos rust-runtime daemon started");
    signal::ctrl_c().await?;
    tracing::info!("omertaos rust-runtime daemon stopping");
    Ok(())
}
