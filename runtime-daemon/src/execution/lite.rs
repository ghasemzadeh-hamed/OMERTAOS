use anyhow::Result;
use std::process::Command;

use crate::execution::backend::ExecutionBackend;
use crate::server::ExecutionContextModel;


pub struct LiteBackend;


impl ExecutionBackend for LiteBackend {

    fn execute(
        &self,
        _ctx: &ExecutionContextModel,
        argv: &[String],
    ) -> Result<(i32,String,String)> {

        if argv.is_empty() {
            anyhow::bail!("command must not be empty");
        }

        let output = Command::new(&argv[0])
            .args(&argv[1..])
            .output()?;


        Ok((
            output.status.code().unwrap_or(-1),
            String::from_utf8_lossy(&output.stdout).to_string(),
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}