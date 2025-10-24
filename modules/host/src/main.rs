use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::process::Command;
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
