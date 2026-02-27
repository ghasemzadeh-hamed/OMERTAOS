use anyhow::Result;

pub struct NamespaceIsolator;

impl NamespaceIsolator {
    pub async fn isolate_process_tree(&self, _pid: u32) -> Result<()> {
        Ok(())
    }
}
