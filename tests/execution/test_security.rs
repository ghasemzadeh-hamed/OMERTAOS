use execution::resource_controller::{ResourceController, ResourceQuota};

#[test]
fn enforce_quota_limits_requests() {
    let controller = ResourceController::default();
    controller.set_quota(
        "agent",
        ResourceQuota {
            cpu_millis: 100,
            memory_mb: 512,
            network_kbps: 2048,
            io_ops: 500,
        },
    );
    let allowed = ResourceQuota { cpu_millis: 50, memory_mb: 256, network_kbps: 1024, io_ops: 100 };
    let denied = ResourceQuota { cpu_millis: 200, memory_mb: 256, network_kbps: 1024, io_ops: 100 };
    assert!(controller.enforce("agent", &allowed));
    assert!(!controller.enforce("agent", &denied));
}
