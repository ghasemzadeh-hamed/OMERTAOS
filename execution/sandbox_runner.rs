//! Backward-compatible sandbox runner wrapper.

pub use crate::runtime::sandbox::{SandboxMode, SandboxRequest, SandboxResult};

pub struct SandboxRunner;

impl SandboxRunner {
    pub fn execute(request: SandboxRequest) -> anyhow::Result<SandboxResult> {
        let sandbox = crate::runtime::sandbox::OsIsolatedSandbox;
        crate::runtime::sandbox::Sandbox::execute(&sandbox, request)
    }
}
