use anyhow::Result;

use crate::{capabilities::CapabilityEnforcer, cgroups::CgroupManager, namespaces::NamespaceIsolator, seccomp::SeccompFilter};

pub struct SandboxRuntime {
    pub cgroups: CgroupManager,
    pub namespaces: NamespaceIsolator,
    pub seccomp: SeccompFilter,
    pub caps: CapabilityEnforcer,
}

impl SandboxRuntime {
    pub async fn enforce(&self, pid: u32) -> Result<()> {
        self.namespaces.isolate_process_tree(pid).await?;
        self.cgroups.apply_limits(pid).await?;
        self.seccomp.install_default_policy(pid).await?;
        self.caps.drop_to_minimal_set(pid).await?;
        Ok(())
    }
}
