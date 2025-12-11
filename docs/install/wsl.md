# WSL installation

AION-OS supports Windows developers through WSL2. Disk actions are skipped; the wizard focuses on profile rendering and service launchers.

## Prerequisites

- Windows 11 with WSL2 enabled (`wsl --install`)
- Ubuntu distribution installed from the Microsoft Store
- Docker Desktop with WSL2 integration enabled
- Windows Terminal or PowerShell with administrator rights

## Steps

1. Open PowerShell as administrator and run `wsl --install -d Ubuntu` if WSL is not already provisioned.
2. Launch the Ubuntu shell, install Git, and set up Docker client utilities (Docker Desktop supplies the daemon):
   ```bash
   sudo apt-get update
   sudo apt-get install -y git
   ```
3. Clone the repository inside the WSL filesystem (`/home/<user>/OMERTAOS`) and change into it.
4. Run `./quick-install.sh` inside WSL to copy `dev.env`, generate development certificates, and start [`docker-compose.quickstart.yml`](../../docker-compose.quickstart.yml) via Docker Desktop.
5. Access the console from Windows at http://localhost:3000 and confirm health at http://localhost:8080/healthz (gateway) and http://localhost:8000/healthz (control).
6. Stop the environment with `docker compose -f docker-compose.quickstart.yml down` when you finish testing.

## Limitations

- GPU passthrough depends on the WSL host capabilities; driver installation commands are skipped automatically.
- Secure Boot and disk encryption are not available inside WSL.
- Snapd is disabled by default inside WSL; the security task logs a warning and continues.
