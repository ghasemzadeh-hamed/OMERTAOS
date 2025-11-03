//! Sandbox runner for executing agent workloads securely.
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

use anyhow::Context;
use serde::{Deserialize, Serialize};
use wasmtime::{Engine, Module, Store, Val};

#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "snake_case")]
pub enum SandboxMode {
    Command { command: String, args: Vec<String> },
    Wasm { module: Vec<u8>, function: String, params: Vec<i32>, fuel: Option<u64> },
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

pub struct SandboxRunner;

impl SandboxRunner {
    pub fn execute(request: SandboxRequest) -> anyhow::Result<SandboxResult> {
        match request.mode {
            SandboxMode::Command { command, args } => Self::execute_command(command, args, request.timeout_secs),
            SandboxMode::Wasm { module, function, params, fuel } => {
                Self::execute_wasm(module, function, params, fuel.unwrap_or(100_000))
            }
        }
    }

    fn execute_command(command: String, args: Vec<String>, timeout_secs: u64) -> anyhow::Result<SandboxResult> {
        let mut child = Command::new(&command)
            .args(&args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .with_context(|| format!("failed to spawn command {command}"))?;

        let timeout = Duration::from_secs(timeout_secs.max(1));
        let start = Instant::now();
        loop {
            if let Some(status) = child.try_wait()? {
                let output = child.wait_with_output()?;
                return Ok(SandboxResult {
                    exit_code: status.code().unwrap_or(-1),
                    stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                    stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                    return_value: None,
                });
            }
            if start.elapsed() >= timeout {
                child.kill().ok();
                return Err(anyhow::anyhow!("sandbox timeout"));
            }
            thread::sleep(Duration::from_millis(25));
        }
    }

    fn execute_wasm(module_bytes: Vec<u8>, function: String, params: Vec<i32>, fuel: u64) -> anyhow::Result<SandboxResult> {
        let mut config = wasmtime::Config::new();
        config.consume_fuel(true);
        let engine = Engine::new(&config)?;
        let module = Module::from_binary(&engine, &module_bytes)
            .or_else(|_| Module::new(&engine, module_bytes))?;
        let mut store = Store::new(&engine, ());
        store.add_fuel(fuel)?;
        let instance = wasmtime::Instance::new(&mut store, &module, &[])?;
        let func = instance
            .get_func(&mut store, &function)
            .context("function not found in module")?;
        let mut results = vec![Val::I32(0)];
        let params_val: Vec<Val> = params.iter().map(|p| Val::I32(*p)).collect();
        func.call(&mut store, &params_val, &mut results)?;
        let value = results
            .get(0)
            .and_then(|v| v.i32())
            .or(Some(0));
        Ok(SandboxResult { exit_code: 0, stdout: String::new(), stderr: String::new(), return_value: value })
    }
}
