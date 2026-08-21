pub mod agent_runner;
pub mod backend;
pub mod command;
pub mod lite;

use anyhow::Result;

use crate::server::ExecutionContextModel;

use backend::ExecutionBackend;
use lite::LiteBackend;


pub fn execute(
    profile: &str,
    ctx: &ExecutionContextModel,
    argv: &[String],
) -> Result<(i32, String, String)> {

    match profile {

        "lite" | "personal" => {
            let backend = LiteBackend;
            backend.execute(ctx, argv)
        }


        "professional" | "enterprise" => {
            command::execute_command(argv)
        }


        _ => {
            anyhow::bail!("unsupported profile")
        }
    }
}