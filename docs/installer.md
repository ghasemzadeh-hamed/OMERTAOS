# Installer Overview

The runtime flake produces a NixOS ISO with containerd and wasmtime preconfigured. To generate the installer image:

```bash
cd runtime
nix build .#nixosConfigurations.aion.config.system.build.isoImage
```

Boot the ISO and run the interactive installer. After installation, push the latest service images to your registry and configure `virtualisation.oci-containers.containers` to pull the appropriate tags.

A systemd unit `containerd.service` launches automatically on boot; use `nerdctl compose up` within `/workspace/OMERTAOS` to start AION.
