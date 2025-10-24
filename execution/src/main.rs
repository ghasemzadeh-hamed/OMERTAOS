use serde_json::json;
use tonic::{transport::Server, Request, Response, Status};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

pub mod aion {
    tonic::include_proto!("aion.execution");
}

use aion::task_executor_server::{TaskExecutor, TaskExecutorServer};
use aion::{TaskRequest, TaskResponse};

#[derive(Default)]
struct ExecutionService;

#[tonic::async_trait]
impl TaskExecutor for ExecutionService {
    async fn execute_task(&self, request: Request<TaskRequest>) -> Result<Response<TaskResponse>, Status> {
        let payload = request.into_inner();
        let parsed: serde_json::Value = serde_json::from_str(&payload.payload).unwrap_or_default();
        let output = match payload.intent.as_str() {
            "summary" => json!({
                "summary": format!("Summarized: {}", parsed),
            }),
            "embedding" => json!({
                "vector": [0.1, 0.2, 0.3]
            }),
            _ => json!({
                "echo": parsed,
            }),
        };

        let reply = TaskResponse {
            external_id: payload.external_id,
            status: "completed".to_string(),
            output: output.to_string(),
        };
        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new("info"))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let addr = "0.0.0.0:50051".parse()?;
    let service = ExecutionService::default();

    Server::builder()
        .add_service(TaskExecutorServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn handles_summary_intent() {
        let service = ExecutionService::default();
        let request = Request::new(TaskRequest {
            external_id: "id".into(),
            intent: "summary".into(),
            payload: "{}".into(),
        });
        let response = service.execute_task(request).await.unwrap();
        assert_eq!(response.into_inner().status, "completed");
    }
}
