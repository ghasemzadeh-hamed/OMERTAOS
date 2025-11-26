# AION-OS Documentation Hub

This directory provides enterprise-ready runbooks covering installation, configuration, and operations across every deployment mode.

## Quick start

See [`quickstart.md`](quickstart.md) for a ten-step launch path across ISO, native Linux, WSL, and Docker modes.

## Installation guides

Mode-specific instructions live under [`install/`](install):

- [`install/iso.md`](install/iso.md)  build and boot the kiosk ISO, including offline cache support.
- [`install/native.md`](install/native.md)  run the installer bridge on an existing Ubuntu host.
- [`install/wsl.md`](install/wsl.md)  bring the stack to Windows via WSL without touching disks.
- [`install/docker.md`](install/docker.md)  compose services for local or CI-driven clusters.

## Profiles and automation

Profile behaviour, feature toggles, and service enablement are described in [`profiles/`](profiles):

- [`profiles/user.md`](profiles/user.md)
- [`profiles/pro.md`](profiles/pro.md)
- [`profiles/enterprise.md`](profiles/enterprise.md)

The installer schema lives in `core/installer/profile/schemas.ts`, and default YAML manifests sit in `core/installer/profile/defaults/`.

## Security and compliance

Baseline hardening, update cadence, and secure boot guidance are documented in [`security/`](security):

- [`security/baseline.md`](security/baseline.md)
- [`security/updates.md`](security/updates.md)
- [`security/secure-boot-fde.md`](security/secure-boot-fde.md)

## Hardware compatibility

GPU, NIC, WiFi, and firmware matrices live in [`hcl/`](hcl). Use [`hcl/index.md`](hcl/index.md) as the entry point, with detail pages for GPUs (`hcl/gpu.md`) and networking (`hcl/nic.md`).

## Operations

- [`troubleshooting.md`](troubleshooting.md)  fixes for common install and runtime issues.
- [`release.md`](release.md)  SBOM, signing, and release validation process.
- [`privacy.md`](privacy.md)  optional telemetry and data handling.
- [`user_team_documentation.md`](user_team_documentation.md)  end-to-end user, admin, and installation guidance with FAQs and glossary.
- [`enterprise_it_infrastructure.md`](enterprise_it_infrastructure.md)  asset inventory, network segmentation, SOPs, DR, IAM, and recovery priorities for enterprise deployments.
- [`full_system_review.md`](full_system_review.md)  architecture, API, install, runbook, security, observability, and DR overview.

---

##  

#   AION-OS

                      .

##  

      ISO   WSL  Docker  [`quickstart.md`](quickstart.md)  .

##  

     [`install/`](install)  :

- [`install/iso.md`](install/iso.md)     ISO     .
- [`install/native.md`](install/native.md)        .
- [`install/wsl.md`](install/wsl.md)        WSL   .
- [`install/docker.md`](install/docker.md)        CI.

##   

        [`profiles/`](profiles)    :

- [`profiles/user.md`](profiles/user.md)
- [`profiles/pro.md`](profiles/pro.md)
- [`profiles/enterprise.md`](profiles/enterprise.md)

   `core/installer/profile/schemas.ts`      YAML  `core/installer/profile/defaults/` .

##   

      Secure Boot  [`security/`](security)  :

- [`security/baseline.md`](security/baseline.md)
- [`security/updates.md`](security/updates.md)
- [`security/secure-boot-fde.md`](security/secure-boot-fde.md)

##  

 GPU NIC     [`hcl/`](hcl)  .  [`hcl/index.md`](hcl/index.md)         GPU (`hcl/gpu.md`)   (`hcl/nic.md`)  .

## 

- [`troubleshooting.md`](troubleshooting.md)        .
- [`release.md`](release.md)   SBOM    .
- [`privacy.md`](privacy.md)      .
- [`user_team_documentation.md`](user_team_documentation.md)          FAQ  .
- [`enterprise_it_infrastructure.md`](enterprise_it_infrastructure.md)      SOP DR IAM      .
- [`full_system_review.md`](full_system_review.md)    API      DR.
