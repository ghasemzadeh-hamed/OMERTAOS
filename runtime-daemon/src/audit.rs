pub fn log_runtime_event(event: &str, tenant_id: &str, agent_id: &str, outcome: &str) {
    tracing::info!(
        event,
        tenant_id,
        agent_id,
        outcome,
        "runtime security event"
    );
}
