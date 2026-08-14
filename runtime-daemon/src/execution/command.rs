use anyhow::Result;

use crate::sandbox::{
    mount::isolate_mounts, namespace::setup_namespaces, process::spawn_isolated,
    seccomp::apply_seccomp,
};

pub fn execute_command(argv: &[String]) -> Result<(i32, String, String)> {
    if argv.is_empty() {
        anyhow::bail!("command must not be empty");
    }
    let joined = argv.join(" ");
    for bad in ["|", ">", "<", "sudo", "&&", ";"] {
        if joined.contains(bad) {
            anyhow::bail!("dangerous pattern blocked");
        }
    }
    setup_namespaces()?;
    isolate_mounts()?;
    apply_seccomp("command")?;
    let _ = spawn_isolated(argv)?;
    Ok((0, String::new(), String::new()))
}
