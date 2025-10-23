fn main() {
    tonic_build::configure()
        .build_client(false)
        .build_server(true)
        .compile(&["proto/execution.proto"], &["proto"])
        .unwrap();
}
