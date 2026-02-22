# aionOS Control Plane

This package provides the control plane services for aionOS. It exposes FastAPI
routes for health checks, memory operations, kernel proposal management, and
model registry interactions.

## Canonical Placement
- Primary implementation is under `os/control/os/*`.
- Plugin/control extension package has been redistributed to `control/aionos_control/*`.
- Legacy compatibility imports remain available at `aionos_control/*` and `os/control/aionos_control/*`.

## Notes
This lightweight README exists so packaging/install flows can resolve the control
modules consistently during CI and local development.
