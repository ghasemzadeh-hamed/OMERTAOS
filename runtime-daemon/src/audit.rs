pub fn log_runtime_event(event: &str, tenant_id: &str, agent_id: &str, outcome: &str) {
    tracing::info!(
        event,
        tenant_id,
        agent_id,
        outcome,
        "runtime security event"
    );
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RuntimeDispatchContext {
    pub tenant_id: String,
    pub task_id: String,
    pub attempt_id: String,
    pub request_id: String,
    pub trace_id: String,
}

pub fn log_runtime_dispatch_event(
    event: &str,
    tenant_id: &str,
    agent_id: &str,
    outcome: &str,
    context: &RuntimeDispatchContext,
) {
    tracing::info!(
        event,
        tenant_id,
        agent_id,
        outcome,
        task_id = context.task_id,
        attempt_id = context.attempt_id,
        request_id = context.request_id,
        trace_id = context.trace_id,
        "runtime dispatch security event"
    );
}
