fn main() {
    tonic_build::configure()
        .build_server(true)
        .compile_protos(&["../schemas/proto/runtime.proto"], &["../schemas/proto"])
        .expect("failed to compile runtime proto");
}
