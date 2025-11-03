use execution::sandbox_runner::{SandboxMode, SandboxRequest, SandboxRunner};

#[test]
fn sandbox_executes_echo() {
    let request = SandboxRequest {
        mode: SandboxMode::Command {
            command: "echo".into(),
            args: vec!["hello".into()],
        },
        timeout_secs: 5,
    };
    let result = SandboxRunner::execute(request).expect("sandbox");
    assert_eq!(result.exit_code, 0);
    assert!(result.stdout.contains("hello"));
}

#[test]
fn sandbox_executes_wasm() {
    let module = wat::parse_str("(module (func (export \"main\") (param i32) (result i32) local.get 0))").unwrap();
    let request = SandboxRequest {
        mode: SandboxMode::Wasm {
            module,
            function: "main".into(),
            params: vec![7],
            fuel: Some(1_000),
        },
        timeout_secs: 5,
    };
    let result = SandboxRunner::execute(request).expect("sandbox wasm");
    assert_eq!(result.return_value, Some(7));
}
