use std::collections::HashMap;
use std::sync::Arc;

use parking_lot::RwLock;
use ring::signature::{self, UnparsedPublicKey};

use crate::contracts::AgentMetadata;

pub trait RegistryService: Send + Sync {
    fn register(&self, metadata: AgentMetadata);
    fn register_with_signature(
        &self,
        metadata: AgentMetadata,
        signature: &[u8],
        public_key: &[u8],
    ) -> anyhow::Result<()>;
    fn get(&self, agent_id: &str) -> Option<AgentMetadata>;
    fn list(&self) -> Vec<AgentMetadata>;
}

#[derive(Clone, Default)]
pub struct InMemoryRegistryService {
    inner: Arc<RwLock<HashMap<String, AgentMetadata>>>,
}

impl RegistryService for InMemoryRegistryService {
    fn register(&self, metadata: AgentMetadata) {
        let mut guard = self.inner.write();
        guard.insert(metadata.agent_id.clone(), metadata);
    }

    fn register_with_signature(
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

    fn get(&self, agent_id: &str) -> Option<AgentMetadata> {
        let guard = self.inner.read();
        guard.get(agent_id).cloned()
    }

    fn list(&self) -> Vec<AgentMetadata> {
        let guard = self.inner.read();
        guard.values().cloned().collect()
    }
}
