//! Optimizer for selecting best agent execution strategy.
use std::collections::HashMap;

use rand::Rng;
use serde::{Deserialize, Serialize};

use crate::agent_registry::AgentMetadata;

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct FeedbackStats {
    pub success: u32,
    pub failure: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OptimizationRequest {
    pub intent: String,
    pub candidates: Vec<AgentMetadata>,
    pub feedback: HashMap<String, FeedbackStats>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OptimizationResult {
    pub selected: Vec<AgentMetadata>,
    pub strategy: String,
}

pub struct AgentOptimizer;

impl AgentOptimizer {
    pub fn optimize(request: OptimizationRequest) -> OptimizationResult {
        let mut rng = rand::thread_rng();
        let mut scored: Vec<(f32, AgentMetadata)> = Vec::new();
        for agent in request.candidates.into_iter() {
            let stats = request.feedback.get(&agent.agent_id).cloned().unwrap_or_default();
            let success_rate = if stats.success + stats.failure == 0 {
                0.5
            } else {
                stats.success as f32 / (stats.success + stats.failure) as f32
            };
            let entropy_bonus: f32 = rng.gen_range(0.0..0.1);
            let capability_bonus = agent.capabilities.len() as f32 * 0.05;
            let score = success_rate + entropy_bonus + capability_bonus;
            scored.push((score, agent));
        }
        scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
        let selected: Vec<AgentMetadata> = scored.into_iter().map(|(_, agent)| agent).take(3).collect();
        OptimizationResult {
            selected,
            strategy: format!("ucb:{}", request.intent),
        }
    }
}
