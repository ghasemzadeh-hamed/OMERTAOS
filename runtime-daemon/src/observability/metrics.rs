use serde_json::json;

pub fn query_metrics(tenant_id: &str) -> String {
    json!({
        "tenant_id": tenant_id,
        "status": "ready"
    })
    .to_string()
}
