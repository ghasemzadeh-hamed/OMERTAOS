{
  description = "AION-OS minimal runtime image";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

  outputs = { self, nixpkgs }: {
    nixosConfigurations.aion = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ({ pkgs, ... }: {
          imports = [
            "${nixpkgs}/nixos/modules/virtualisation/containerd.nix"
          ];
          services.openssh.enable = true;
          services.containerd.enable = true;
          services.containerd.settings = {
            version = 2;
            plugins."io.containerd.grpc.v1.cri".containerd = {
              snapshotter = "overlayfs";
              default_runtime_name = "runc";
              runtimes.wasmtime = {
                runtime_type = "io.containerd.wasmtime.v1";
              };
            };
          };
          virtualisation.oci-containers.containers = {
            gateway = {
              image = "aion-gateway:latest";
            };
            control = {
              image = "aion-control:latest";
            };
            execution = {
              image = "aion-execution:latest";
            };
            web = {
              image = "aion-web:latest";
            };
          };
          environment.systemPackages = with pkgs; [
            containerd
            crictl
            wasmtime
            nerdctl
          ];
          system.stateVersion = "24.05";
        })
      ];
    };
  };
}
