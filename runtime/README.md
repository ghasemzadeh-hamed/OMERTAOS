# AION Runtime Layer

This directory contains a NixOS flake that assembles a bootable minimal image with containerd, a WASM runtime, and the AION service stack.

## Building the ISO

```bash
nix build .#nixosConfigurations.aion.config.system.build.isoImage
```

The resulting ISO includes containerd configured with both runc and wasmtime runtimes and declares the AION containers via the OCI container module.

## Boot Sequence

1. Containerd starts with the configured runtimes.
2. `nerdctl compose up` launches the gateway, control plane, execution engine, and web console containers.
3. The WASM runtime is available for future OCI/WASM agent deployments.
