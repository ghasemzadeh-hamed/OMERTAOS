use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct RuntimeConfig {
    pub bind_addr: String,
    pub profile: String,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            bind_addr: std::env::var("AION_RUNTIME_BIND_ADDR")
                .unwrap_or_else(|_| "127.0.0.1:50051".to_string()),
            profile: std::env::var("OMERTA_PROFILE").unwrap_or_else(|_| "lite".to_string()),
        }
    }
}
