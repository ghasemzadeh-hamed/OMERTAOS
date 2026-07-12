fn main() {
    let protoc = protoc_bin_vendored::protoc_bin_path().expect("failed to find vendored protoc");
    std::env::set_var("PROTOC", protoc);

    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(
            &["../schemas/v1/protos/runtime.proto"],
            &["../schemas/v1/protos"],
        )
        .expect("failed to compile runtime proto");
}
