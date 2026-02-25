use std::sync::Arc;

use tracing::{error, info, instrument};

use crate::runtime::queue::TaskQueue;
use crate::runtime::sandbox::{OsIsolatedSandbox, Sandbox, SandboxMode, SandboxRequest};

pub struct Worker {
    queue: Arc<dyn TaskQueue>,
    sandbox: Arc<dyn Sandbox>,
}

impl Worker {
    pub fn new(queue: Arc<dyn TaskQueue>) -> Self {
        Self {
            queue,
            sandbox: Arc::new(OsIsolatedSandbox),
        }
    }

    pub fn with_sandbox(queue: Arc<dyn TaskQueue>, sandbox: Arc<dyn Sandbox>) -> Self {
        Self { queue, sandbox }
    }

    #[instrument(skip(self))]
    pub fn run_once(&self) {
        let Some(task) = self.queue.pop() else {
            info!("queue is empty");
            return;
        };

        let request = SandboxRequest {
            mode: SandboxMode::Command {
                command: task.command,
                args: task.args,
                cgroup: Some(format!("omertaos/{}", task.agent_id)),
            },
            timeout_secs: task.timeout_secs,
        };

        match self.sandbox.execute(request) {
            Ok(result) => info!(task_id = %task.task_id, exit_code = result.exit_code, "task executed"),
            Err(err) => error!(task_id = %task.task_id, error = %err, "task execution failed"),
        }
    }
}
