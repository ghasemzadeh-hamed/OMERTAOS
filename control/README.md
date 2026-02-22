# aionOS Control Plane

This package provides the control plane services for aionOS. It exposes FastAPI
routes for health checks, memory operations, kernel proposal management, and
model registry interactions.

## Canonical Placement
- Primary implementation is under `os/control/os/*`.
- Plugin/control extension package has been redistributed to `control/aion_control/*`.
- Legacy compatibility imports remain available at `aion_control/*` and `os/control/aion_control/*`.

## Notes
This lightweight README exists so packaging/install flows can resolve the control
modules consistently during CI and local development.
