# Enterprise profile

The enterprise profile includes the full MLOps stack, directory integration, and a hardened baseline.

## Services

- Gateway, control plane, and console enabled
- MLflow and Jupyter enabled for experimentation and tracking
- Docker and Kubernetes hooks enabled
- LDAP integration enabled for centralized auth (expect to configure `ldap.conf` post-install)

## Security

- Hardening level: `cis-lite`
- UFW, Fail2Ban, and Auditd enabled automatically
- Secure Boot and full-disk encryption recommended (toggle in the wizard storage step)

## Post-install steps

1. Configure LDAP details in `/etc/ldap/ldap.conf` and restart related services.
2. Deploy Kubernetes manifests or connect to your cluster using the generated kubeconfig.
3. Review `/var/log/aionos-firstboot.log` for audit entries and confirm `auditd` is active.
