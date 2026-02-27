use anyhow::Result;

pub struct CgroupManager;

impl CgroupManager {
    pub async fn apply_limits(&self, _pid: u32) -> Result<()> {
        Ok(())
    }
}
