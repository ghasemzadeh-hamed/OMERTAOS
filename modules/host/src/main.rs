use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::process::Command;
#[cfg(target_os = "linux")]
use std::os::unix::process::CommandExt;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[derive(Debug, Deserialize)]
struct ExecuteRequest {
    module: String,
    payload: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct ExecuteResponse {
    status: String,
    output: serde_json::Value,
}

fn main() -> Result<()> {
    let subscriber = FmtSubscriber::builder().with_max_level(Level::INFO).finish();
    tracing::subscriber::set_global_default(subscriber).expect("setting default subscriber failed");
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("usage: module_host <module> <payload>");
        std::process::exit(1);
    }
    let module = &args[1];
    let payload: serde_json::Value = serde_json::from_str(&args[2])?;
    let response = execute_subprocess(module, &payload)?;
    println!("{}", serde_json::to_string(&response)?);
    Ok(())
}

fn execute_subprocess(module: &str, payload: &serde_json::Value) -> Result<ExecuteResponse> {
    info!(module, "Launching subprocess module");
    let mut cmd = Command::new(module);
    cmd.arg(payload.to_string());
    #[cfg(target_os = "linux")]
    {
        let seccomp_profile = std::env::var("AION_MODULE_SECCOMP_PROFILE")
            .ok()
            .filter(|value| !value.is_empty())
            .or_else(|| Some(String::from("config/seccomp/module-default.json")));
        let apparmor_profile = std::env::var("AION_MODULE_APPARMOR_PROFILE")
            .ok()
            .filter(|value| !value.is_empty());
        cmd.before_exec(move || sandbox::apply(seccomp_profile.clone(), apparmor_profile.clone()));
    }
    let output = cmd.output()?;
    if !output.status.success() {
        return Ok(ExecuteResponse {
            status: "error".into(),
            output: serde_json::json!({"stderr": String::from_utf8_lossy(&output.stderr)}),
        });
    }
    let stdout = String::from_utf8_lossy(&output.stdout);
    let json_output: serde_json::Value = serde_json::from_str(&stdout).unwrap_or_else(|_| serde_json::json!({"raw": stdout}));
    Ok(ExecuteResponse {
        status: "ok".into(),
        output: json_output,
    })
}

#[cfg(target_os = "linux")]
mod sandbox {
    use std::fs;
    use std::io::{self, Error, ErrorKind};
    use std::path::Path;

    use seccompiler::{apply_filter, compile_from_json, TargetArch};
    use tracing::warn;

    #[cfg(target_arch = "x86_64")]
    const ARCH: TargetArch = TargetArch::X86_64;
    #[cfg(target_arch = "aarch64")]
    const ARCH: TargetArch = TargetArch::Aarch64;

    pub fn apply(seccomp_profile: Option<String>, apparmor_profile: Option<String>) -> io::Result<()> {
        if let Some(profile) = apparmor_profile {
            if let Err(err) = fs::write("/proc/self/attr/exec", profile.as_bytes()) {
                warn!(?err, "failed to set AppArmor profile");
            }
        }
        if let Some(profile) = seccomp_profile {
            let path = Path::new(&profile);
            if !path.exists() {
                warn!(%profile, "seccomp profile not found");
                return Ok(());
            }
            let file = fs::File::open(path)?;
            let filters = compile_from_json(file, ARCH)
                .map_err(|err| Error::new(ErrorKind::Other, err.to_string()))?;
            if let Some(filter) = filters.get("default") {
                apply_filter(filter.as_slice())
                    .map_err(|err| Error::new(ErrorKind::Other, err.to_string()))?;
            } else {
                warn!(%profile, "seccomp profile missing default filter");
            }
        }
        Ok(())
    }
}

#[cfg(not(target_os = "linux"))]
mod sandbox {
    use std::io;

    pub fn apply(_seccomp_profile: Option<String>, _apparmor_profile: Option<String>) -> io::Result<()> {
        Ok(())
    }
}
