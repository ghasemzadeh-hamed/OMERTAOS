use anyhow::Result;

pub fn apply_seccomp(_profile: &str) -> Result<()> {
    anyhow::bail!("seccomp backend is not implemented; execution denied")
}
