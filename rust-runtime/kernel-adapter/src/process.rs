use anyhow::Result;

pub struct ProcessBridge;

impl ProcessBridge {
    pub async fn spawn_sandboxed(&self, _cmd: &str, _args: &[String]) -> Result<u32> {
        Ok(0)
    }
}
