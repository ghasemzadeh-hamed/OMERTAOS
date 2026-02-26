use anyhow::Result;
use nix::unistd::Pid;

pub fn spawn_isolated(_argv: &[String]) -> Result<Pid> {
    Ok(Pid::from_raw(1))
}
