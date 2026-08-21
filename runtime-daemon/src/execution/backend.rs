use crate::server::ExecutionContextModel;

pub trait ExecutionBackend {
    fn execute(
        &self,
        ctx: &ExecutionContextModel,
        argv: &[String],
    ) -> anyhow::Result<(i32, String, String)>;
}
