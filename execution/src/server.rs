use std::net::SocketAddr;

use serde_json::{json, Value};
use tonic::{transport::Server, Request, Response, Status};

use self::proto::task_module_server::{TaskModule, TaskModuleServer};
use self::proto::{TaskReply, TaskRequest};

pub mod proto {
    tonic::include_proto!("aion.execution");
}

#[derive(Default)]
pub struct ModuleService;

#[tonic::async_trait]
impl TaskModule for ModuleService {
    async fn execute(&self, request: Request<TaskRequest>) -> Result<Response<TaskReply>, Status> {
        let payload = request.into_inner();
        let params: Value = serde_json::from_str(&payload.payload_json).unwrap_or(Value::Null);

        let (status, result_json) = if payload.intent.to_lowercase().contains("summarize") {
            let text = params
                .get("text")
                .and_then(|value| value.as_str())
                .unwrap_or("");
            let summary = text.split('.').next().unwrap_or("").trim();
            (
                "completed".to_string(),
                serde_json::to_string(&json!({
                    "summary": summary,
                    "original_length": text.len()
                }))
                .unwrap(),
            )
        } else {
            (
                "completed".to_string(),
                serde_json::to_string(&json!({
                    "echo": params,
                    "intent": payload.intent
                }))
                .unwrap(),
            )
        };

        Ok(Response::new(TaskReply {
            status,
            result_json,
        }))
    }
}

pub async fn serve() -> Result<(), Box<dyn std::error::Error>> {
    let addr: SocketAddr = "0.0.0.0:50051".parse()?;
    let service = ModuleService::default();

    Server::builder()
        .add_service(TaskModuleServer::new(service))
        .serve(addr)
        .await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn summarize_intent_returns_summary() {
        let service = ModuleService::default();
        let request = TaskRequest {
            task_id: "1".into(),
            intent: "summarize report".into(),
            payload_json: serde_json::to_string(&json!({ "text": "Hello world. This is AION." })).unwrap(),
        };
        let response = service.execute(Request::new(request)).await.unwrap();
        let reply = response.into_inner();
        assert_eq!(reply.status, "completed");
        let result: Value = serde_json::from_str(&reply.result_json).unwrap();
        assert_eq!(result.get("summary").unwrap(), "Hello world");
    }
}
