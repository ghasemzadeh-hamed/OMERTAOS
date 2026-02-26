fn main() {
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(&["../shared/proto/runtime.proto"], &["../shared/proto"])
        .expect("failed to compile runtime proto");
}
