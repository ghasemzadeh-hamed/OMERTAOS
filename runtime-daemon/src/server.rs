use std::sync::Arc;

use anyhow::Result;
use tonic::metadata::MetadataMap;
use tonic::{Request, Response, Status};

use crate::audit::{log_runtime_dispatch_event, log_runtime_event, RuntimeDispatchContext};
use crate::config::RuntimeConfig;
use crate::execution::{agent_runner::run_agent, execute};
use crate::observability::metrics::query_metrics;
use crate::security::capability::validate_capabilities;

#[allow(clippy::result_large_err)]
pub mod pb {
    tonic::include_proto!("runtime");
}

#[derive(Debug, Clone)]
pub struct ExecutionContextModel {
    pub agent_id: String,
    pub tenant_id: String,
    pub cpu_cores: u32,
    pub memory_mb: u64,
    pub gpu_enabled: bool,
    pub capabilities: Vec<String>,
}

impl TryFrom<pb::ExecutionContext> for ExecutionContextModel {
    type Error = Status;

    fn try_from(value: pb::ExecutionContext) -> std::result::Result<Self, Self::Error> {
        if value.agent_id.is_empty() || value.tenant_id.is_empty() {
            return Err(Status::invalid_argument(
                "agent_id and tenant_id are required",
            ));
        }
        Ok(Self {
            agent_id: value.agent_id,
            tenant_id: value.tenant_id,
            cpu_cores: value.cpu_cores,
            memory_mb: value.memory_mb,
            gpu_enabled: value.gpu_enabled,
            capabilities: value.capabilities,
        })
    }
}

#[derive(Debug)]
pub struct RuntimeServiceImpl {
    config: Arc<RuntimeConfig>,
}

impl RuntimeServiceImpl {
    pub fn new(config: RuntimeConfig) -> Self {
        Self {
            config: Arc::new(config),
        }
    }

    pub fn service(self) -> pb::runtime_service_server::RuntimeServiceServer<Self> {
        pb::runtime_service_server::RuntimeServiceServer::new(self)
    }
}

#[tonic::async_trait]
impl pb::runtime_service_server::RuntimeService for RuntimeServiceImpl {
    async fn start_agent(
        &self,
        request: Request<pb::StartAgentRequest>,
    ) -> std::result::Result<Response<pb::StartAgentResponse>, Status> {
        let req = request.into_inner();
        let ctx = req
            .context
            .ok_or_else(|| Status::invalid_argument("context is required"))?
            .try_into()?;
        validate_capabilities(&ctx, &["agent.start"]).map_err(map_error)?;
        log_runtime_event("agent.start", &ctx.tenant_id, &ctx.agent_id, "authorized");
        let pid = run_agent(&ctx, &self.config.profile, &req.argv).map_err(map_error)?;
        Ok(Response::new(pb::StartAgentResponse {
            ok: true,
            message: "started".into(),
            pid,
        }))
    }

    async fn stop_agent(
        &self,
        _request: Request<pb::StopAgentRequest>,
    ) -> std::result::Result<Response<pb::StopAgentResponse>, Status> {
        Ok(Response::new(pb::StopAgentResponse {
            ok: true,
            message: "stopped".into(),
        }))
    }

    async fn allocate_resources(
        &self,
        request: Request<pb::ResourceRequest>,
    ) -> std::result::Result<Response<pb::ResourceResponse>, Status> {
        let req = request.into_inner();
        let ctx: ExecutionContextModel = req
            .context
            .ok_or_else(|| Status::invalid_argument("context is required"))?
            .try_into()?;
        if req.profile.is_empty() || req.profile != self.config.profile {
            return Err(Status::invalid_argument("profile mismatch"));
        }
        validate_capabilities(&ctx, &["resource.allocate"]).map_err(map_error)?;
        log_runtime_event(
            "resource.allocate",
            &ctx.tenant_id,
            &ctx.agent_id,
            "authorized",
        );
        Ok(Response::new(pb::ResourceResponse {
            ok: true,
            message: "allocated".into(),
        }))
    }

    async fn execute_command(
        &self,
        request: Request<pb::CommandRequest>,
    ) -> std::result::Result<Response<pb::CommandResponse>, Status> {
        let dispatch_context = dispatch_context(request.metadata());
        let req = request.into_inner();
        let ctx: ExecutionContextModel = req
            .context
            .ok_or_else(|| Status::invalid_argument("context is required"))?
            .try_into()?;
        if !dispatch_tenant_matches(&ctx, &dispatch_context) {
            return Err(Status::permission_denied(
                "tenant metadata does not match execution context",
            ));
        }
        validate_capabilities(&ctx, &["terminal.execute"]).map_err(map_error)?;
        log_runtime_dispatch_event(
            "terminal.execute",
            &ctx.tenant_id,
            &ctx.agent_id,
            "authorized",
            &dispatch_context,
        );
        let execution = execute(&self.config.profile, &ctx, &req.argv);
        let (code, stdout, stderr) = match execution {
            Ok(result) => {
                log_runtime_dispatch_event(
                    "terminal.execute",
                    &ctx.tenant_id,
                    &ctx.agent_id,
                    "completed",
                    &dispatch_context,
                );
                result
            }
            Err(error) => {
                log_runtime_dispatch_event(
                    "terminal.execute",
                    &ctx.tenant_id,
                    &ctx.agent_id,
                    "failed",
                    &dispatch_context,
                );
                return Err(map_error(error));
            }
        };
        Ok(Response::new(pb::CommandResponse {
            ok: code == 0,
            stdout,
            stderr,
            code,
        }))
    }

    async fn query_metrics(
        &self,
        request: Request<pb::MetricsRequest>,
    ) -> std::result::Result<Response<pb::MetricsResponse>, Status> {
        let req = request.into_inner();
        Ok(Response::new(pb::MetricsResponse {
            ok: true,
            json: query_metrics(&req.tenant_id),
        }))
    }
}

fn dispatch_context(metadata: &MetadataMap) -> RuntimeDispatchContext {
    RuntimeDispatchContext {
        tenant_id: metadata_value(metadata, "tenant-id"),
        task_id: metadata_value(metadata, "x-aion-task-id"),
        attempt_id: metadata_value(metadata, "x-aion-attempt-id"),
        request_id: metadata_value(metadata, "x-request-id"),
        trace_id: metadata_value(metadata, "traceparent"),
    }
}

fn metadata_value(metadata: &MetadataMap, key: &'static str) -> String {
    metadata
        .get(key)
        .and_then(|value| value.to_str().ok())
        .unwrap_or_default()
        .to_owned()
}

fn dispatch_tenant_matches(
    execution: &ExecutionContextModel,
    dispatch: &RuntimeDispatchContext,
) -> bool {
    dispatch.tenant_id.is_empty() || dispatch.tenant_id == execution.tenant_id
}

fn map_error(err: anyhow::Error) -> Status {
    Status::internal(err.to_string())
}

pub async fn run_server(config: RuntimeConfig) -> Result<()> {
    let addr = config.bind_addr.parse()?;
    tonic::transport::Server::builder()
        .add_service(RuntimeServiceImpl::new(config).service())
        .serve_with_shutdown(addr, shutdown_signal())
        .await?;
    Ok(())
}

async fn shutdown_signal() {
    #[cfg(unix)]
    {
        use tokio::signal::unix::{signal, SignalKind};

        let mut terminate = signal(SignalKind::terminate())
            .expect("failed to install SIGTERM handler for runtime daemon");
        tokio::select! {
            _ = tokio::signal::ctrl_c() => {
                tracing::info!("runtime daemon received SIGINT");
            }
            _ = terminate.recv() => {
                tracing::info!("runtime daemon received SIGTERM");
            }
        }
    }

    #[cfg(not(unix))]
    {
        if let Err(err) = tokio::signal::ctrl_c().await {
            tracing::warn!(%err, "runtime daemon shutdown signal handler failed");
        }
    }
}

#[cfg(test)]
mod tests {
    use tonic::metadata::MetadataValue;

    use super::*;

    #[test]
    fn dispatch_context_reads_grpc_metadata_fields() {
        let mut metadata = MetadataMap::new();
        metadata.insert("tenant-id", MetadataValue::from_static("tenant-a"));
        metadata.insert("x-aion-task-id", MetadataValue::from_static("task-a"));
        metadata.insert("x-aion-attempt-id", MetadataValue::from_static("task-a:0"));
        metadata.insert("x-request-id", MetadataValue::from_static("request-a"));
        metadata.insert(
            "traceparent",
            MetadataValue::from_static("00-trace-a-span-a-01"),
        );

        assert_eq!(
            dispatch_context(&metadata),
            RuntimeDispatchContext {
                tenant_id: "tenant-a".into(),
                task_id: "task-a".into(),
                attempt_id: "task-a:0".into(),
                request_id: "request-a".into(),
                trace_id: "00-trace-a-span-a-01".into(),
            }
        );
    }

    #[test]
    fn dispatch_tenant_must_match_execution_context() {
        let execution = ExecutionContextModel {
            agent_id: "agent-a".into(),
            tenant_id: "tenant-a".into(),
            cpu_cores: 0,
            memory_mb: 0,
            gpu_enabled: false,
            capabilities: vec!["terminal.execute".into()],
        };
        let matching = RuntimeDispatchContext {
            tenant_id: "tenant-a".into(),
            ..RuntimeDispatchContext::default()
        };
        let mismatched = RuntimeDispatchContext {
            tenant_id: "tenant-b".into(),
            ..RuntimeDispatchContext::default()
        };

        assert!(dispatch_tenant_matches(&execution, &matching));
        assert!(!dispatch_tenant_matches(&execution, &mismatched));
    }
}
