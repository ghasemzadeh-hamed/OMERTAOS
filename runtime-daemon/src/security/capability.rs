use anyhow::Result;

use crate::server::ExecutionContextModel;

pub fn validate_capabilities(ctx: &ExecutionContextModel, required: &[&str]) -> Result<()> {
    for cap in required {
        if !ctx.capabilities.iter().any(|c| c == cap) {
            anyhow::bail!("missing capability: {}", cap);
        }
    }
    Ok(())
}
