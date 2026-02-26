use anyhow::Result;

use crate::server::ExecutionContextModel;

pub fn apply_cpu_limits(ctx: &ExecutionContextModel) -> Result<()> {
    if ctx.cpu_cores == 0 {
        anyhow::bail!("cpu_cores must be > 0");
    }
    Ok(())
}
