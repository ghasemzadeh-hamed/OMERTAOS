# Hardware compatibility list

This HCL focuses on Ubuntu AI class systems. Compatibility is validated on each release branch.

## GPUs

See [`gpu.md`](gpu.md) for detailed firmware and driver notes.

## Networking

See [`nic.md`](nic.md) for NIC and Wi-Fi status.

## Reporting

1. Collect `lspci -nn`, `lsblk`, and `dmesg` output.
2. Attach `/var/log/aionos-installer.log` and `/var/log/aionos-firstboot.log`.
3. File an issue or submit the bundle to the hardware enablement email alias.
