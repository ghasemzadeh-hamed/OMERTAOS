use anyhow::Result;
use nix::unistd::Pid;

pub fn spawn_isolated(_argv: &[String]) -> Result<Pid> {
    anyhow::bail!("isolated process backend is not implemented; execution denied")
}
