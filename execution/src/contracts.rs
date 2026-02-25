use std::collections::HashMap;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentMetadata {
    pub agent_id: String,
    pub version: String,
    pub capabilities: Vec<String>,
    pub resources: HashMap<String, String>,
    pub digest: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskEnvelope {
    pub task_id: String,
    pub agent_id: String,
    pub command: String,
    pub args: Vec<String>,
    pub timeout_secs: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub accepted: bool,
    pub reason: Option<String>,
}
