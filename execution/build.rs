fn main() {
    tonic_build::configure()
        .build_server(true)
        .compile(&["proto/aion.proto"], &["proto"])
        .expect("Failed to compile protos");
}
