# GPU compatibility

| Vendor | Models | Status | Notes |
| --- | --- | --- | --- |
| NVIDIA | RTX 4090, A100, L4 | Supported | Uses `ubuntu-drivers autoinstall`; secure boot requires MOK enrolment |
| AMD | Radeon PRO W6800, MI210 | Supported | Installs `firmware-amd-graphics`; ROCm optional |
| Intel | Arc A770, Iris Xe | Supported | Installs `intel-media-va-driver-non-free`; ensure BIOS Resizable BAR is enabled |

## Troubleshooting

- Use `nvidia-smi` / `rocminfo` / `intel_gpu_top` to confirm runtime status.
- Check `/var/log/aionos-firstboot.log` for install errors.
- Secure Boot: sign DKMS modules when prompted to avoid boot failures.
