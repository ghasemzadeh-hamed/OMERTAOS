# NIC and Wi-Fi compatibility

| Vendor   | Device                 | Status    | Packages                             |
| -------- | ---------------------- | --------- | ------------------------------------ |
| Intel    | X710, AX211            | Supported | `firmware-iwlwifi`, `linux-firmware` |
| Realtek  | RTL8125, RTL8852AE     | Supported | `firmware-realtek`                   |
| Mellanox | ConnectX-5, ConnectX-6 | Supported | `mlx5-tools`                         |

## Tips

- Run `ethtool -i <interface>` to confirm driver binding.
- For Wi-Fi, ensure regulatory domain is set via `iw reg set`.
- Firmware packages install during the driver task; check `/var/log/aionos-installer.log` for confirmation.
