use tracing::info;

pub fn log_runtime_event(event: &str, tenant_id: &str, agent_id: &str) {
    info!(event = event, tenant_id = tenant_id, agent_id = agent_id, "kernel adapter audit event");
}
