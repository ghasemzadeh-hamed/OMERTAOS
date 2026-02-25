use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

use anyhow::Context;
use serde::{Deserialize, Serialize};
use tracing::{debug, info, instrument, warn};
use wasmtime::{Engine, Module, Store, Val};

#[cfg(target_os = "linux")]
use std::os::unix::process::CommandExt;

#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "snake_case")]
pub enum SandboxMode {
    Command {
        command: String,
        args: Vec<String>,
        cgroup: Option<String>,
    },
    Wasm {
        module: Vec<u8>,
        function: String,
        params: Vec<i32>,
        fuel: Option<u64>,
    },
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SandboxRequest {
    pub mode: SandboxMode,
    pub timeout_secs: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SandboxResult {
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
    pub return_value: Option<i32>,
}

pub trait Sandbox: Send + Sync {
    fn execute(&self, request: SandboxRequest) -> anyhow::Result<SandboxResult>;
}

pub struct OsIsolatedSandbox;

impl Sandbox for OsIsolatedSandbox {
    #[instrument(skip(self, request), fields(timeout_secs = request.timeout_secs))]
    fn execute(&self, request: SandboxRequest) -> anyhow::Result<SandboxResult> {
        match request.mode {
            SandboxMode::Command {
                command,
                args,
                cgroup,
            } => execute_command(command, args, cgroup, request.timeout_secs),
            SandboxMode::Wasm {
                module,
                function,
                params,
                fuel,
            } => execute_wasm(module, function, params, fuel.unwrap_or(100_000)),
        }
    }
}

#[instrument(fields(command = %command))]
fn execute_command(
    command: String,
    args: Vec<String>,
    cgroup: Option<String>,
    timeout_secs: u64,
) -> anyhow::Result<SandboxResult> {
    let mut cmd = Command::new(&command);
    cmd.args(&args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    #[cfg(target_os = "linux")]
    {
        unsafe {
            cmd.pre_exec(|| {
                // strict seccomp mode: allow only read/write/_exit/sigreturn.
                let rc = libc::prctl(libc::PR_SET_SECCOMP, libc::SECCOMP_MODE_STRICT);
                if rc != 0 {
                    return Err(std::io::Error::last_os_error());
                }
                Ok(())
            });
        }
    }

    let mut child = cmd
        .spawn()
        .with_context(|| format!("failed to spawn command {command}"))?;

    #[cfg(target_os = "linux")]
    {
        if let Some(group) = cgroup {
            let cgroup_procs = format!("/sys/fs/cgroup/{group}/cgroup.procs");
            std::fs::write(&cgroup_procs, child.id().to_string())
                .with_context(|| format!("failed to attach process to cgroup path {cgroup_procs}"))?;
            info!(path = %cgroup_procs, pid = child.id(), "attached workload to cgroup");
        }
    }

    let timeout = Duration::from_secs(timeout_secs.max(1));
    let start = Instant::now();
    loop {
        if let Some(status) = child.try_wait()? {
            let output = child.wait_with_output()?;
            info!(exit = status.code().unwrap_or(-1), "sandboxed command finished");
            return Ok(SandboxResult {
                exit_code: status.code().unwrap_or(-1),
                stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                return_value: None,
            });
        }
        if start.elapsed() >= timeout {
            warn!("sandbox timeout reached; killing process");
            child.kill().ok();
            return Err(anyhow::anyhow!("sandbox timeout"));
        }
        debug!(elapsed_ms = start.elapsed().as_millis(), "waiting for sandbox process");
        thread::sleep(Duration::from_millis(25));
    }
}

#[instrument(skip(module_bytes, params), fields(function = %function, fuel = fuel))]
fn execute_wasm(
    module_bytes: Vec<u8>,
    function: String,
    params: Vec<i32>,
    fuel: u64,
) -> anyhow::Result<SandboxResult> {
    let mut config = wasmtime::Config::new();
    config.consume_fuel(true);
    let engine = Engine::new(&config)?;
    let module =
        Module::from_binary(&engine, &module_bytes).or_else(|_| Module::new(&engine, module_bytes))?;
    let mut store = Store::new(&engine, ());
    store.add_fuel(fuel)?;
    let instance = wasmtime::Instance::new(&mut store, &module, &[])?;
    let func = instance
        .get_func(&mut store, &function)
        .context("function not found in module")?;
    let mut results = vec![Val::I32(0)];
    let params_val: Vec<Val> = params.iter().map(|p| Val::I32(*p)).collect();
    func.call(&mut store, &params_val, &mut results)?;
    let value = results.first().and_then(|v| v.i32()).or(Some(0));

    Ok(SandboxResult {
        exit_code: 0,
        stdout: String::new(),
        stderr: String::new(),
        return_value: value,
    })
}
