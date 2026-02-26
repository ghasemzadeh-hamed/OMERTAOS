use anyhow::Result;

use crate::server::ExecutionContextModel;

pub fn bind_gpu(ctx: &ExecutionContextModel, profile: &str) -> Result<()> {
    if profile == "lite" && ctx.gpu_enabled {
        anyhow::bail!("gpu is disabled in lite profile");
    }
    if ctx.gpu_enabled {
        let nvidia_exists = std::path::Path::new("/proc/driver/nvidia").exists();
        if !nvidia_exists {
            anyhow::bail!("gpu requested but nvidia driver not detected");
        }
    }
    Ok(())
}
