//! Resource controller manages compute allocations for agents.
use std::collections::HashMap;
use std::sync::Arc;

use parking_lot::Mutex;

#[derive(Clone, Debug, Default)]
pub struct ResourceQuota {
    pub cpu_millis: u32,
    pub memory_mb: u32,
    pub network_kbps: u32,
    pub io_ops: u32,
}

#[derive(Clone, Default)]
pub struct ResourceController {
    quotas: Arc<Mutex<HashMap<String, ResourceQuota>>>,
}

impl ResourceController {
    pub fn set_quota(&self, agent_id: &str, quota: ResourceQuota) {
        let mut guard = self.quotas.lock();
        guard.insert(agent_id.to_string(), quota);
    }

    pub fn get_quota(&self, agent_id: &str) -> Option<ResourceQuota> {
        let guard = self.quotas.lock();
        guard.get(agent_id).cloned()
    }

    pub fn enforce(&self, agent_id: &str, request: &ResourceQuota) -> bool {
        match self.get_quota(agent_id) {
            Some(quota) => {
                request.cpu_millis <= quota.cpu_millis
                    && request.memory_mb <= quota.memory_mb
                    && request.network_kbps <= quota.network_kbps
                    && request.io_ops <= quota.io_ops
            }
            None => true,
        }
    }
}
