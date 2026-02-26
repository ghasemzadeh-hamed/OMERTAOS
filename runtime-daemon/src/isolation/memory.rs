use anyhow::Result;

use crate::server::ExecutionContextModel;

pub fn apply_memory_limits(ctx: &ExecutionContextModel) -> Result<()> {
    if ctx.memory_mb == 0 {
        anyhow::bail!("memory_mb must be > 0");
    }
    Ok(())
}
