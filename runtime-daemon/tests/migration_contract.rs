use runtime_daemon::cluster::{
    node_registration::register_node, resource_report::report_resources,
};
use runtime_daemon::isolation::quota::ResourceQuota;
use runtime_daemon::sandbox::{mount, namespace, process, seccomp};

#[test]
fn resource_quota_requires_positive_limits() {
    assert!(ResourceQuota {
        cpu_millis: 100,
        memory_bytes: 1024,
        pids_max: 8,
    }
    .validate()
    .is_ok());

    for invalid in [
        ResourceQuota {
            cpu_millis: 0,
            memory_bytes: 1024,
            pids_max: 8,
        },
        ResourceQuota {
            cpu_millis: 100,
            memory_bytes: 0,
            pids_max: 8,
        },
        ResourceQuota {
            cpu_millis: 100,
            memory_bytes: 1024,
            pids_max: 0,
        },
    ] {
        assert!(invalid.validate().is_err());
    }
}

#[test]
fn incomplete_sandbox_backends_fail_closed() {
    assert!(namespace::setup_namespaces().is_err());
    assert!(mount::isolate_mounts().is_err());
    assert!(seccomp::apply_seccomp("test").is_err());
    assert!(process::spawn_isolated(&["echo".to_string()]).is_err());
}

#[test]
fn cluster_node_registration_rejects_blank_identifiers() {
    assert!(register_node("runtime-a"));
    assert!(!register_node(""));
    assert!(!register_node("   "));
}

#[test]
fn resource_report_advertises_node_capacity_and_capabilities() {
    let report = report_resources();

    assert!(report.contains("\"node_id\""));
    assert!(report.contains("\"total_cpu_millis\""));
    assert!(report.contains("\"available_memory_mb\""));
    assert!(report.contains("\"capabilities\""));
    assert_ne!(report, "{}");
}
