fn main() {
    let protoc = protoc_bin_vendored::protoc_bin_path().expect("failed to find vendored protoc");
    std::env::set_var("PROTOC", protoc);

    tonic_build::configure()
        .build_server(true)
        .compile_protos(&["../schemas/proto/runtime.proto"], &["../schemas/proto"])
        .expect("failed to compile runtime proto");
}
