#[tokio::main]
async fn main() -> anyhow::Result<()> {
    runtime_daemon::run().await
}
