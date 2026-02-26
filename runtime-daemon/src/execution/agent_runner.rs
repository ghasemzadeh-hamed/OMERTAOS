use anyhow::Result;

use crate::isolation::{cpu::apply_cpu_limits, gpu::bind_gpu, memory::apply_memory_limits};
use crate::sandbox::{mount::isolate_mounts, namespace::setup_namespaces, process::spawn_isolated, seccomp::apply_seccomp};
use crate::server::ExecutionContextModel;

pub fn run_agent(ctx: &ExecutionContextModel, profile: &str, argv: &[String]) -> Result<i64> {
    apply_cpu_limits(ctx)?;
    apply_memory_limits(ctx)?;
    bind_gpu(ctx, profile)?;
    setup_namespaces()?;
    isolate_mounts()?;
    apply_seccomp("agent")?;
    let pid = spawn_isolated(argv)?;
    Ok(pid.as_raw() as i64)
}
