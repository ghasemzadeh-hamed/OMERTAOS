use anyhow::Result;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ResourceQuota {
    pub cpu_millis: u64,
    pub memory_bytes: u64,
    pub pids_max: u64,
}

impl ResourceQuota {
    pub fn validate(&self) -> Result<()> {
        if self.cpu_millis == 0 {
            anyhow::bail!("cpu_millis must be positive");
        }
        if self.memory_bytes == 0 {
            anyhow::bail!("memory_bytes must be positive");
        }
        if self.pids_max == 0 {
            anyhow::bail!("pids_max must be positive");
        }
        Ok(())
    }
}
