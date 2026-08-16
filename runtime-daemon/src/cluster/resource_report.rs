pub fn report_resources() -> String {
    let node_id =
        std::env::var("AION_RUNTIME_NODE_ID").unwrap_or_else(|_| "runtime-local-1".to_string());
    let profile = std::env::var("OMERTA_PROFILE").unwrap_or_else(|_| "lite".to_string());
    let memory_mb = std::env::var("AION_RUNTIME_MEMORY_MB")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(512);
    let cpu_millis = std::thread::available_parallelism()
        .map(|parallelism| parallelism.get() as u64 * 1000)
        .unwrap_or(1000);
    let capabilities = std::env::var("AION_RUNTIME_CAPABILITIES")
        .unwrap_or_else(|_| "resource.allocate".to_string());
    let capability_json = capabilities
        .split(',')
        .map(str::trim)
        .filter(|capability| !capability.is_empty())
        .map(|capability| format!("\"{}\"", escape_json(capability)))
        .collect::<Vec<_>>()
        .join(",");

    format!(
        "{{\"node_id\":\"{}\",\"profile\":\"{}\",\"total_cpu_millis\":{},\"available_cpu_millis\":{},\"total_memory_mb\":{},\"available_memory_mb\":{},\"capabilities\":[{}]}}",
        escape_json(&node_id),
        escape_json(&profile),
        cpu_millis,
        cpu_millis,
        memory_mb,
        memory_mb,
        capability_json
    )
}

fn escape_json(value: &str) -> String {
    value.replace('\\', "\\\\").replace('"', "\\\"")
}
