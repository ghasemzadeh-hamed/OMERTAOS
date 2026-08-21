use std::sync::Arc;

use anyhow::Result;
use tonic::{Request, Response, Status};

use crate::audit::log_runtime_event;
use crate::config::RuntimeConfig;
use crate::execution::{
    execute,
    agent_runner::run_agent
};
use crate::observability::metrics::query_metrics;
use crate::security::capability::validate_capabilities;

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
        let req = request.into_inner();
        let ctx: ExecutionContextModel = req
            .context
            .ok_or_else(|| Status::invalid_argument("context is required"))?
            .try_into()?;
        validate_capabilities(&ctx, &["terminal.execute"]).map_err(map_error)?;
        log_runtime_event(
            "terminal.execute",
            &ctx.tenant_id,
            &ctx.agent_id,
            "authorized",
        );
        let (code, stdout, stderr) =
            execute(
                &self.config.profile,
                &ctx,
                &req.argv,
            )
    .map_err(map_error)?;
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
