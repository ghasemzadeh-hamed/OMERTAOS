use std::collections::HashMap;
use std::sync::Mutex;

use thiserror::Error;

const MIN_TOKEN_LENGTH: usize = 32;
const MAX_TOKEN_LENGTH: usize = 128;

#[derive(Debug, Error, PartialEq, Eq)]
pub enum LeaseError {
    #[error("lease metadata is incomplete")]
    Incomplete,
    #[error("lease metadata is malformed")]
    Malformed,
    #[error("lease targets a different runtime node")]
    NodeMismatch,
    #[error("lease is expired")]
    Expired,
    #[error("lease expiry exceeds the runtime bound")]
    ExcessiveTtl,
    #[error("lease generation is stale or already claimed")]
    Stale,
    #[error("lease fence state is unavailable")]
    StateUnavailable,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LeaseClaim {
    pub tenant_id: String,
    pub task_id: String,
    pub attempt_id: String,
    pub node_id: String,
    pub generation: u64,
    pub expires_at_ms: u64,
}

impl LeaseClaim {
    pub fn parse(
        tenant_id: &str,
        task_id: &str,
        attempt_id: &str,
        node_id: &str,
        token: &str,
        generation: &str,
        expires_at_ms: &str,
    ) -> Result<Self, LeaseError> {
        if [
            tenant_id,
            task_id,
            attempt_id,
            node_id,
            token,
            generation,
            expires_at_ms,
        ]
        .iter()
        .any(|value| value.is_empty())
        {
            return Err(LeaseError::Incomplete);
        }
        if token.len() < MIN_TOKEN_LENGTH
            || token.len() > MAX_TOKEN_LENGTH
            || !token
                .bytes()
                .all(|value| value.is_ascii_alphanumeric() || value == b'-' || value == b'_')
        {
            return Err(LeaseError::Malformed);
        }
        let generation = generation.parse().map_err(|_| LeaseError::Malformed)?;
        let expires_at_ms = expires_at_ms.parse().map_err(|_| LeaseError::Malformed)?;
        if generation == 0 || expires_at_ms == 0 {
            return Err(LeaseError::Malformed);
        }
        Ok(Self {
            tenant_id: tenant_id.to_owned(),
            task_id: task_id.to_owned(),
            attempt_id: attempt_id.to_owned(),
            node_id: node_id.to_owned(),
            generation,
            expires_at_ms,
        })
    }

    fn fence_key(&self) -> String {
        format!("{}\0{}", self.tenant_id, self.task_id)
    }
}

#[derive(Debug, Default)]
pub struct LeaseFence {
    generations: Mutex<HashMap<String, u64>>,
}

impl LeaseFence {
    pub fn claim(
        &self,
        claim: &LeaseClaim,
        expected_node_id: &str,
        now_ms: u64,
        max_ttl_seconds: u64,
    ) -> Result<(), LeaseError> {
        if claim.node_id != expected_node_id {
            return Err(LeaseError::NodeMismatch);
        }
        if claim.expires_at_ms <= now_ms {
            return Err(LeaseError::Expired);
        }
        let max_expiry = now_ms.saturating_add(max_ttl_seconds.saturating_mul(1000));
        if claim.expires_at_ms > max_expiry {
            return Err(LeaseError::ExcessiveTtl);
        }
        let mut generations = self
            .generations
            .lock()
            .map_err(|_| LeaseError::StateUnavailable)?;
        let key = claim.fence_key();
        if generations
            .get(&key)
            .is_some_and(|current| *current >= claim.generation)
        {
            return Err(LeaseError::Stale);
        }
        generations.insert(key, claim.generation);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn claim(generation: u64, expires_at_ms: u64) -> LeaseClaim {
        LeaseClaim::parse(
            "tenant-a",
            "task-a",
            &format!("task-a:{generation}"),
            "runtime-a",
            "abcdefghijklmnopqrstuvwxyzABCDEFG_1234567890",
            &generation.to_string(),
            &expires_at_ms.to_string(),
        )
        .unwrap()
    }

    #[test]
    fn claims_once_and_fences_older_generations() {
        let fence = LeaseFence::default();
        let first = claim(10, 20_000);
        let newer = claim(11, 20_000);

        assert_eq!(fence.claim(&first, "runtime-a", 10_000, 30), Ok(()));
        assert_eq!(
            fence.claim(&first, "runtime-a", 10_000, 30),
            Err(LeaseError::Stale)
        );
        assert_eq!(fence.claim(&newer, "runtime-a", 10_000, 30), Ok(()));
        assert_eq!(
            fence.claim(&first, "runtime-a", 10_000, 30),
            Err(LeaseError::Stale)
        );
    }

    #[test]
    fn rejects_expired_wrong_node_and_excessive_ttl() {
        let fence = LeaseFence::default();
        let expired = claim(1, 10_000);
        let future = claim(2, 100_000);

        assert_eq!(
            fence.claim(&expired, "runtime-a", 10_000, 30),
            Err(LeaseError::Expired)
        );
        assert_eq!(
            fence.claim(&future, "runtime-b", 10_000, 120),
            Err(LeaseError::NodeMismatch)
        );
        assert_eq!(
            fence.claim(&future, "runtime-a", 10_000, 30),
            Err(LeaseError::ExcessiveTtl)
        );
    }

    #[test]
    fn rejects_missing_or_malformed_metadata() {
        assert_eq!(
            LeaseClaim::parse("", "task", "attempt", "node", "token", "1", "2"),
            Err(LeaseError::Incomplete)
        );
        assert_eq!(
            LeaseClaim::parse("tenant", "task", "attempt", "node", "short", "one", "two"),
            Err(LeaseError::Malformed)
        );
    }
}
