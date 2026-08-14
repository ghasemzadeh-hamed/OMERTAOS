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
