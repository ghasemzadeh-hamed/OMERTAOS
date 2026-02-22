# User profile

The user profile targets lightweight developer workstations.

## Services

- Gateway, control plane, and console enabled
- Optional services (MLflow, Jupyter, Docker, Kubernetes hooks, LDAP) disabled

## Security

- Hardening level: `none`
- First boot still applies security updates and firmware refreshes

## Post-install steps

1. Source the rendered `.env` file and adjust any local ports.
2. Enable additional services manually if needed (`systemctl enable aion-mlflow.service`).
3. Review `/var/log/aion-firstboot.log` to confirm updates completed.
