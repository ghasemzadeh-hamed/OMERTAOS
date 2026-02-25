use tracing_subscriber::{fmt, EnvFilter};

pub fn init_tracing(service_name: &str) {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = fmt()
        .with_env_filter(filter)
        .json()
        .with_target(true)
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_current_span(true)
        .with_span_list(true)
        .try_init();

    tracing::info!(service = service_name, "tracing initialized");
}
