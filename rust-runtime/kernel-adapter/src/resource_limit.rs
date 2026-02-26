#[derive(Debug, Clone)]
pub struct ResourceQuota {
    pub cpu_millis: u64,
    pub memory_bytes: u64,
    pub pids_max: u64,
}
