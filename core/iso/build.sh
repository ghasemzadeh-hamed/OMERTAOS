#!/usr/bin/env bash
set -euo pipefail

# Requires running on an Ubuntu host with the following packages installed:
#   sudo apt-get install -y \
#     debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools genisoimage rsync
# The script assembles a hybrid BIOS/UEFI ISO that boots into an Ubuntu-based live
# environment with Calamares, the AION-OS installer UI, and the OMERTAOS stack baked in.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
BUILD="$ROOT/build"
CHROOT="$BUILD/chroot"
ISO_TREE="$BUILD/iso"

UBUNTU_CODENAME="jammy"
ARCH="amd64"
MIRROR_URL="http://archive.ubuntu.com/ubuntu"

rm -rf "$BUILD"
mkdir -p "$BUILD" "$CHROOT" "$ISO_TREE"

# 1) Bootstrap a minimal Ubuntu system inside the chroot.
sudo debootstrap --arch="$ARCH" "$UBUNTU_CODENAME" "$CHROOT" "$MIRROR_URL"

# 2) Install runtime requirements, desktop/installer tooling, and language stacks.
sudo chroot "$CHROOT" /bin/bash <<'EOF_CHROOT'
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  systemd-sysv linux-image-generic \
  grub-efi-amd64-signed shim-signed \
  casper lupin-casper \
  calamares calamares-settings-ubuntu \
  network-manager \
  xfsprogs btrfs-progs \
  openssh-server sudo \
  git curl wget \
  software-properties-common \
  pciutils usbutils dmidecode \
  dkms linux-firmware ubuntu-drivers-common \
  python3 python3-venv python3-pip \
  nodejs npm

# live session user
id -u aionos >/dev/null 2>&1 || useradd -m -s /bin/bash aionos
if ! getent group sudo | grep -q '\baionos\b'; then
  adduser aionos sudo
fi
if ! printf '%s\n' "aionos:aionos" | chpasswd 2>/dev/null; then
  echo "warning: unable to update default password" >&2
fi
EOF_CHROOT

# 3) Copy installer UI, system services, and first-boot assets into the chroot.
sudo mkdir -p "$CHROOT/etc/calamares" "$CHROOT/usr/local/aionos-firstboot" "$CHROOT/etc/systemd/system"
sudo rsync -a "$ROOT/installer-ui/" "$CHROOT/etc/calamares/"
sudo rsync -a "$ROOT/firstboot/" "$CHROOT/usr/local/aionos-firstboot/"
sudo rsync -a "$ROOT/systemd/" "$CHROOT/etc/systemd/system/"

# 4) Copy the repository itself so systemd units can run locally.
sudo mkdir -p "$CHROOT/opt/omertaos"
sudo rsync -a \
  --exclude '/core/build' \
  --exclude '.git' \
  --exclude '.github' \
  --exclude 'node_modules' \
  "$REPO_ROOT/" "$CHROOT/opt/omertaos/"

# 5) Produce the squashfs filesystem image.
mkdir -p "$ISO_TREE/casper" "$ISO_TREE/EFI/boot" "$ISO_TREE/boot/grub"
sudo mksquashfs "$CHROOT" "$ISO_TREE/casper/filesystem.squashfs" -e boot

# 6) Copy kernel and initrd artifacts from the chroot.
KERNEL=$(cd "$CHROOT/boot" && ls vmlinuz-* | head -n1)
INITRD=$(cd "$CHROOT/boot" && ls initrd.img-* | head -n1)
sudo cp "$CHROOT/boot/$KERNEL" "$ISO_TREE/casper/vmlinuz"
sudo cp "$CHROOT/boot/$INITRD" "$ISO_TREE/casper/initrd"

# 7) Write a simple GRUB configuration for the live environment.
cat > "$ISO_TREE/boot/grub/grub.cfg" <<'EOF_GRUB'
set default=0
set timeout=5

menuentry "AION-OS Installer" {
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}
EOF_GRUB

# 8) Build the hybrid ISO with grub-mkrescue.
ISO_OUT="$ROOT/../aionos-installer.iso"
grub-mkrescue -o "$ISO_OUT" "$ISO_TREE" --compress=xz

echo "ISO built at: $ISO_OUT"
