use anyhow::Result;

pub struct SeccompFilter;

impl SeccompFilter {
    pub async fn install_default_policy(&self, _pid: u32) -> Result<()> {
        Ok(())
    }
}
