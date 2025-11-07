# Pro profile

The pro profile serves small teams that require core MLOps tooling without enterprise directory integration.

## Services

- Gateway, control plane, and console enabled
- MLflow and Jupyter services enabled
- Docker support enabled for local workflows
- Kubernetes hooks disabled by default
- LDAP integration disabled

## Security

- Hardening level: `standard`
- UFW and Fail2Ban are enabled during first boot

## Post-install steps

1. Access MLflow at the configured port (default 5000) and bind notebooks to team workspaces.
2. Configure Docker users (`sudo usermod -aG docker <user>`).
3. Review `/var/log/aionos-firstboot.log` for driver installation status.
