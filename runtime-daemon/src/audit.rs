pub fn log_runtime_event(event: &str, tenant_id: &str, agent_id: &str, outcome: &str) {
    tracing::info!(
        event,
        tenant_id,
        agent_id,
        outcome,
        "runtime security event"
    );
}

#[derive(Clone, Default, PartialEq, Eq)]
pub struct RuntimeDispatchContext {
    pub tenant_id: String,
    pub task_id: String,
    pub attempt_id: String,
    pub request_id: String,
    pub trace_id: String,
    pub node_id: String,
    pub lease_token: String,
    pub lease_generation: String,
    pub lease_expires_at_ms: String,
}

impl std::fmt::Debug for RuntimeDispatchContext {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter
            .debug_struct("RuntimeDispatchContext")
            .field("tenant_id", &self.tenant_id)
            .field("task_id", &self.task_id)
            .field("attempt_id", &self.attempt_id)
            .field("request_id", &self.request_id)
            .field("trace_id", &self.trace_id)
            .field("node_id", &self.node_id)
            .field("lease_token", &"[REDACTED]")
            .field("lease_generation", &self.lease_generation)
            .field("lease_expires_at_ms", &self.lease_expires_at_ms)
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dispatch_context_debug_redacts_the_lease_token() {
        let context = RuntimeDispatchContext {
            lease_token: "sensitive-lease-token-that-must-not-appear".into(),
            ..RuntimeDispatchContext::default()
        };

        let rendered = format!("{context:?}");

        assert!(rendered.contains("[REDACTED]"));
        assert!(!rendered.contains("sensitive-lease-token-that-must-not-appear"));
    }
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
        node_id = context.node_id,
        lease_generation = context.lease_generation,
        lease_expires_at_ms = context.lease_expires_at_ms,
        "runtime dispatch security event"
    );
}
