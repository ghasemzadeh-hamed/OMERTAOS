use anyhow::Result;

pub struct CapabilityEnforcer;

impl CapabilityEnforcer {
    pub async fn drop_to_minimal_set(&self, _pid: u32) -> Result<()> {
        Ok(())
    }
}
