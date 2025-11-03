//! Registry for execution plane agents with signature verification.
use std::collections::HashMap;
use std::sync::Arc;

use parking_lot::RwLock;
use ring::signature::{self, UnparsedPublicKey};
use serde::{Deserialize, Serialize};
use serde_json;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentMetadata {
    pub agent_id: String,
    pub version: String,
    pub capabilities: Vec<String>,
    pub resources: HashMap<String, String>,
    pub digest: String,
}

#[derive(Clone, Default)]
pub struct AgentRegistry {
    inner: Arc<RwLock<HashMap<String, AgentMetadata>>>,
}

impl AgentRegistry {
    pub fn register(&self, metadata: AgentMetadata) {
        let mut guard = self.inner.write();
        guard.insert(metadata.agent_id.clone(), metadata);
    }

    pub fn register_with_signature(
        &self,
        metadata: AgentMetadata,
        signature: &[u8],
        public_key: &[u8],
    ) -> anyhow::Result<()> {
        let verifier = UnparsedPublicKey::new(&signature::ED25519, public_key);
        let message = serde_json::to_vec(&metadata)?;
        verifier
            .verify(&message, signature)
            .map_err(|_| anyhow::anyhow!("signature verification failed"))?;
        self.register(metadata);
        Ok(())
    }

    pub fn get(&self, agent_id: &str) -> Option<AgentMetadata> {
        let guard = self.inner.read();
        guard.get(agent_id).cloned()
    }

    pub fn list(&self) -> Vec<AgentMetadata> {
        let guard = self.inner.read();
        guard.values().cloned().collect()
    }
}
