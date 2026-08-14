use anyhow::Result;

pub fn validate_signature(signature: &str) -> Result<()> {
    if signature.is_empty() {
        anyhow::bail!("empty signature");
    }
    Ok(())
}
